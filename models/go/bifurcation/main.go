/*
Cooperation Threshold Bifurcation Analysis

High-performance Go implementation of the critical mass threshold analysis
from Theorem 4.2 (Voluntary Cooperation Stability).

Tests different initial cooperation rates to find which converge to
cooperation vs defection equilibrium, identifying the critical threshold.

Key dynamics:
- Agents have intrinsic motivation M_i to cooperate
- Cooperation cost c, benefit from k cooperators: beta*k/n
- Cooperation is rational when: M_i > c - beta*k/n
- Critical mass theta_crit determines stability
- Network effects can reinforce cooperation above threshold
*/

package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"math"
	"math/rand"
	"os"
	"runtime"
	"sync"
	"time"
)

// Agent represents a citizen deciding whether to cooperate
type Agent struct {
	BaseMotivation float64
	Motivation     float64
	Cooperating    bool
	Transformed    bool
}

// SimParams holds simulation parameters
type SimParams struct {
	NAgents             int     `json:"n_agents"`
	NSteps              int     `json:"n_steps"`
	CooperationCost     float64 `json:"cooperation_cost"`
	BenefitMultiplier   float64 `json:"benefit_multiplier"`
	MotivationMean      float64 `json:"motivation_mean"`
	MotivationStd       float64 `json:"motivation_std"`
	InitialCooperation  float64 `json:"initial_cooperation"`
	TransformedFraction float64 `json:"transformed_fraction"`
	TransformationBoost float64 `json:"transformation_boost"`
	NetworkEffects      bool    `json:"network_effects"`
	NetworkStrength     float64 `json:"network_strength"`
	MotivationDynamics  bool    `json:"motivation_dynamics"`
	ReinforcementRate   float64 `json:"reinforcement_rate"`
	DiscouragementRate  float64 `json:"discouragement_rate"`
	DecisionNoise       float64 `json:"decision_noise"`
}

// BifurcationResult holds the result of a single run
type BifurcationResult struct {
	InitialRate float64 `json:"initial_rate"`
	FinalRate   float64 `json:"final_rate"`
	ThetaCrit   float64 `json:"theta_crit"`
	Replication int     `json:"replication"`
}

// BifurcationOutput holds all results
type BifurcationOutput struct {
	Results   []BifurcationResult `json:"results"`
	ThetaCrit float64             `json:"theta_crit"`
}

// DefaultParams returns sensible default parameters
func DefaultParams() SimParams {
	return SimParams{
		NAgents:             1000,
		NSteps:              100,
		CooperationCost:     1.0,
		BenefitMultiplier:   2.0,
		MotivationMean:      0.5,
		MotivationStd:       0.3,
		InitialCooperation:  0.5,
		TransformedFraction: 0.0,
		TransformationBoost: 1.0,
		NetworkEffects:      true,
		NetworkStrength:     0.5,
		MotivationDynamics:  true,
		ReinforcementRate:   0.02,
		DiscouragementRate:  0.01,
		DecisionNoise:       0.1,
	}
}

// Simulate runs a single cooperation threshold simulation
func Simulate(params SimParams, rng *rand.Rand) float64 {
	// Initialize agents
	agents := make([]Agent, params.NAgents)
	nTransformed := int(float64(params.NAgents) * params.TransformedFraction)

	for i := range agents {
		// Draw motivation from distribution
		baseMot := math.Max(0, rng.NormFloat64()*params.MotivationStd+params.MotivationMean)

		// Apply transformation boost to some agents
		var motivation float64
		var transformed bool
		if i < nTransformed {
			motivation = baseMot + params.TransformationBoost
			transformed = true
		} else {
			motivation = baseMot
			transformed = false
		}

		agents[i] = Agent{
			BaseMotivation: baseMot,
			Motivation:     motivation,
			Cooperating:    rng.Float64() < params.InitialCooperation,
			Transformed:    transformed,
		}
	}

	// Run simulation
	for step := 0; step < params.NSteps; step++ {
		// Shuffle agent order
		rng.Shuffle(len(agents), func(i, j int) {
			agents[i], agents[j] = agents[j], agents[i]
		})

		// Get current cooperation rate
		nCooperators := 0
		for _, a := range agents {
			if a.Cooperating {
				nCooperators++
			}
		}
		cooperationRate := float64(nCooperators) / float64(params.NAgents)

		// Update each agent
		for i := range agents {
			// Calculate threshold for cooperation
			// From Theorem 4.2: cooperate if M_i > c - beta*theta
			threshold := params.CooperationCost - params.BenefitMultiplier*cooperationRate

			// Network effects: seeing others cooperate boosts motivation
			effectiveMotivation := agents[i].Motivation
			if params.NetworkEffects {
				socialBoost := params.NetworkStrength * cooperationRate
				effectiveMotivation += socialBoost
			}

			// Decision with some noise (bounded rationality)
			noise := rng.NormFloat64() * params.DecisionNoise
			agents[i].Cooperating = (effectiveMotivation + noise) > threshold

			// Update motivation based on experience
			if params.MotivationDynamics {
				if agents[i].Cooperating {
					if cooperationRate > 0.5 {
						// Cooperation reinforced in cooperative environment
						newMot := agents[i].Motivation * (1 + params.ReinforcementRate)
						agents[i].Motivation = math.Min(newMot, agents[i].BaseMotivation*2)
					} else {
						// Discouragement when cooperating alone
						agents[i].Motivation *= (1 - params.DiscouragementRate)
					}
				} else {
					// Gradual return to base motivation when defecting
					agents[i].Motivation = agents[i].Motivation*0.99 + agents[i].BaseMotivation*0.01
				}
			}
		}
	}

	// Calculate final cooperation rate
	nCooperators := 0
	for _, a := range agents {
		if a.Cooperating {
			nCooperators++
		}
	}

	return float64(nCooperators) / float64(params.NAgents)
}

// RunBifurcationAnalysis runs the full bifurcation sweep in parallel
func RunBifurcationAnalysis(params SimParams, initialRates []float64, nReplications, numWorkers int) BifurcationOutput {
	// Calculate critical threshold
	thetaCrit := params.CooperationCost / (params.BenefitMultiplier + params.MotivationMean)

	// Create all jobs
	type job struct {
		initRate int // index into initialRates
		rep      int
	}

	totalJobs := len(initialRates) * nReplications
	jobs := make([]job, totalJobs)
	idx := 0
	for i := range initialRates {
		for rep := 0; rep < nReplications; rep++ {
			jobs[idx] = job{initRate: i, rep: rep}
			idx++
		}
	}

	// Results slice
	results := make([]BifurcationResult, totalJobs)

	// Run in parallel
	var wg sync.WaitGroup
	chunkSize := (totalJobs + numWorkers - 1) / numWorkers

	for w := 0; w < numWorkers; w++ {
		start := w * chunkSize
		end := start + chunkSize
		if end > totalJobs {
			end = totalJobs
		}
		if start >= totalJobs {
			break
		}

		wg.Add(1)
		go func(start, end int) {
			defer wg.Done()
			// Each goroutine gets its own RNG
			rng := rand.New(rand.NewSource(time.Now().UnixNano() + int64(start)))

			for i := start; i < end; i++ {
				j := jobs[i]
				initRate := initialRates[j.initRate]

				// Create params with this initial rate
				runParams := params
				runParams.InitialCooperation = initRate

				// Run simulation
				finalRate := Simulate(runParams, rng)

				results[i] = BifurcationResult{
					InitialRate: initRate,
					FinalRate:   finalRate,
					ThetaCrit:   thetaCrit,
					Replication: j.rep,
				}
			}
		}(start, end)
	}

	wg.Wait()

	return BifurcationOutput{
		Results:   results,
		ThetaCrit: thetaCrit,
	}
}

func main() {
	// Command line flags
	nAgents := flag.Int("n", 1000, "Number of agents")
	nSteps := flag.Int("steps", 100, "Simulation steps per run")
	nReps := flag.Int("reps", 5, "Replications per initial rate")
	nRates := flag.Int("rates", 17, "Number of initial rates to test")
	workers := flag.Int("workers", 0, "Number of parallel workers (0 = auto)")
	output := flag.String("output", "", "Output file path (empty = stdout)")

	// Model parameters
	coopCost := flag.Float64("cost", 1.0, "Cooperation cost")
	benefit := flag.Float64("benefit", 2.0, "Benefit multiplier")
	motMean := flag.Float64("mot-mean", 0.5, "Motivation mean")
	motStd := flag.Float64("mot-std", 0.3, "Motivation std dev")
	networkStr := flag.Float64("network", 0.5, "Network strength")
	noise := flag.Float64("noise", 0.1, "Decision noise")

	flag.Parse()

	// Set workers
	numWorkers := *workers
	if numWorkers <= 0 {
		numWorkers = runtime.NumCPU()
	}

	// Create parameters
	params := SimParams{
		NAgents:            *nAgents,
		NSteps:             *nSteps,
		CooperationCost:    *coopCost,
		BenefitMultiplier:  *benefit,
		MotivationMean:     *motMean,
		MotivationStd:      *motStd,
		NetworkEffects:     true,
		NetworkStrength:    *networkStr,
		MotivationDynamics: true,
		ReinforcementRate:  0.02,
		DiscouragementRate: 0.01,
		DecisionNoise:      *noise,
	}

	// Generate initial rates
	initialRates := make([]float64, *nRates)
	for i := range initialRates {
		initialRates[i] = 0.1 + 0.8*float64(i)/float64(*nRates-1)
	}

	// Run analysis
	fmt.Fprintf(os.Stderr, "Running bifurcation analysis: %d rates x %d reps = %d runs with %d workers\n",
		*nRates, *nReps, (*nRates)*(*nReps), numWorkers)

	start := time.Now()
	results := RunBifurcationAnalysis(params, initialRates, *nReps, numWorkers)
	elapsed := time.Since(start)

	fmt.Fprintf(os.Stderr, "Completed in %v\n", elapsed)
	fmt.Fprintf(os.Stderr, "Critical threshold theta_crit = %.3f\n", results.ThetaCrit)

	// Output results
	jsonData, err := json.MarshalIndent(results, "", "  ")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error encoding JSON: %v\n", err)
		os.Exit(1)
	}

	if *output != "" {
		err = os.WriteFile(*output, jsonData, 0644)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error writing file: %v\n", err)
			os.Exit(1)
		}
		fmt.Fprintf(os.Stderr, "Results written to %s\n", *output)
	} else {
		fmt.Println(string(jsonData))
	}
}
