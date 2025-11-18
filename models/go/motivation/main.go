/*
Motivation Foundations Model

Tests the hypothesis that sustainable cooperation requires soteriological foundations
rather than purely institutional cultivation of motivation.

Two motivation sources:
1. Institutional M_i: Derived from collective-choice, reputation, social pressure
   - Decays when institution degrades (corruption spreads)
   - Creates feedback loop: degradation → M_i drop → more corruption

2. Soteriological M_i: Derived from transcendent values
   - Independent of institutional state
   - May increase under adversity (martyrdom/witness effect)
   - Provides stable foundation for cooperation

Key prediction: Over sufficiently long time horizons, only soteriological foundations
maintain cooperation. Institutional cultivation either fails or converges to
soteriological forms (finding transcendent meaning in cooperation itself).
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

// MotivationSource indicates the foundation of an agent's motivation
type MotivationSource int

const (
	SourceInstitutional MotivationSource = iota
	SourceSoteriological
	SourceMixed
)

// Participant represents an agent with motivation foundations
type Participant struct {
	BaseMotivation       float64
	InstitutionalBoost   float64
	SoteriologicalCore   float64
	EffectiveMotivation  float64
	Cooperating          bool
	Source               MotivationSource
}

// SimParams holds simulation parameters
type SimParams struct {
	NAgents int `json:"n_agents"`
	NSteps  int `json:"n_steps"`

	// Motivation parameters
	BaseMotivationMean float64 `json:"base_motivation_mean"`
	BaseMotivationStd  float64 `json:"base_motivation_std"`

	// Institutional motivation
	InstitutionalBoostMax    float64 `json:"institutional_boost_max"`
	InstitutionalDecayRate   float64 `json:"institutional_decay_rate"`
	InstitutionalGrowthRate  float64 `json:"institutional_growth_rate"`
	CorruptionThreshold      float64 `json:"corruption_threshold"`

	// Soteriological motivation
	SoteriologicalFraction   float64 `json:"soteriological_fraction"`
	SoteriologicalCoreMean   float64 `json:"soteriological_core_mean"`
	SoteriologicalCoreStd    float64 `json:"soteriological_core_std"`
	AdversityBoostRate       float64 `json:"adversity_boost_rate"`
	MaxAdversityBoost        float64 `json:"max_adversity_boost"`

	// Cooperation dynamics
	CooperationCost     float64 `json:"cooperation_cost"`
	BenefitMultiplier   float64 `json:"benefit_multiplier"`
	NetworkStrength     float64 `json:"network_strength"`
	DecisionNoise       float64 `json:"decision_noise"`

	// Critical threshold
	ThetaCrit float64 `json:"theta_crit"`

	// Exogenous shocks
	ShockProbability float64 `json:"shock_probability"`
	ShockMagnitude   float64 `json:"shock_magnitude"`

	// Scale effects (Dunbar to intergalactic)
	OptimalScale        float64 `json:"optimal_scale"`         // Dunbar-like optimal (~150)
	ScaleDecayRate      float64 `json:"scale_decay_rate"`      // How fast institutions degrade with scale
	EnableScaleEffects  bool    `json:"enable_scale_effects"`
}

// SimResult holds time series results
type SimResult struct {
	CooperationRates     []float64 `json:"cooperation_rates"`
	MeanMotivations      []float64 `json:"mean_motivations"`
	InstitutionalHealth  []float64 `json:"institutional_health"`
	FinalCooperationRate float64   `json:"final_cooperation_rate"`
	StableCooperation    bool      `json:"stable_cooperation"`
	CyclesTillCollapse   int       `json:"cycles_till_collapse"`
}

// scaleEffectMultiplier calculates how much institutional mechanisms are degraded by scale
// This degradation emerges from explicit mechanisms, not assumption:
//
// 1. MONITORING COSTS: In group of N, potential pairs = N(N-1)/2 = O(N²)
//    Each person can track ~150 relationships (Dunbar cognitive limit)
//    Monitoring effectiveness per person = min(1, optimalScale/N)
//
// 2. REPUTATION RELIABILITY: Beyond direct observation, information passes through
//    gossip chains. Each hop degrades signal. Chain length ~ log(N)/log(optimalScale)
//    Reliability = (1-noise)^chainLength
//
// 3. SOCIAL PRESSURE DIFFUSION: Shame/praise from strangers < from close relations
//    Effective social pressure = fraction of group within Dunbar limit
//    = optimalScale/N for N > optimalScale
//
// 4. FREE-RIDER DETECTION: Probability of being observed decreases with group size
//    Detection prob ~ optimalScale/N (assuming fixed observation capacity)
//
// Combined effect: These mechanisms multiply together, giving approximately
// exponential decay beyond optimal scale.
func scaleEffectMultiplier(n int, optimalScale, decayRate float64) float64 {
	if float64(n) <= optimalScale {
		return 1.0
	}

	nf := float64(n)

	// Monitoring effectiveness: can only track optimalScale relationships
	// Effectiveness = optimalScale / N
	monitoringEff := optimalScale / nf

	// Reputation chain length: information hops ~ log(N/optimalScale)
	// Assuming 10% noise per hop
	chainLength := math.Log(nf/optimalScale) / math.Log(2) // binary tree approximation
	reputationReliability := math.Pow(0.9, chainLength)

	// Social pressure: fraction of meaningful relationships
	socialPressure := optimalScale / nf

	// Free-rider detection: inverse of hiding opportunity
	detectionProb := optimalScale / nf

	// Combined effect (geometric mean to avoid over-penalizing)
	combined := math.Pow(monitoringEff*reputationReliability*socialPressure*detectionProb, 0.25)

	// Apply decay rate as sensitivity parameter
	return math.Pow(combined, decayRate)
}

// Simulate runs a single long-horizon simulation
func Simulate(params SimParams, rng *rand.Rand) SimResult {
	// Calculate scale effect on institutional mechanisms
	scaleMult := 1.0
	if params.EnableScaleEffects {
		scaleMult = scaleEffectMultiplier(params.NAgents, params.OptimalScale, params.ScaleDecayRate)
	}

	// Effective parameters after scale degradation
	effectiveBoostMax := params.InstitutionalBoostMax * scaleMult
	effectiveNetworkStr := params.NetworkStrength * scaleMult
	effectiveGrowthRate := params.InstitutionalGrowthRate * scaleMult

	// Initialize agents
	agents := make([]Participant, params.NAgents)
	nSoteriological := int(float64(params.NAgents) * params.SoteriologicalFraction)

	for i := range agents {
		baseMot := math.Max(0.1, rng.NormFloat64()*params.BaseMotivationStd+params.BaseMotivationMean)

		if i < nSoteriological {
			// Soteriological foundation - NOT affected by scale
			soterio := math.Max(0.1, rng.NormFloat64()*params.SoteriologicalCoreStd+params.SoteriologicalCoreMean)
			agents[i] = Participant{
				BaseMotivation:      baseMot,
				InstitutionalBoost:  0,
				SoteriologicalCore:  soterio,
				EffectiveMotivation: baseMot + soterio,
				Cooperating:         true, // Start cooperating
				Source:              SourceSoteriological,
			}
		} else {
			// Institutional foundation - degraded by scale
			agents[i] = Participant{
				BaseMotivation:      baseMot,
				InstitutionalBoost:  effectiveBoostMax * 0.5, // Start with some boost
				SoteriologicalCore:  0,
				EffectiveMotivation: baseMot + effectiveBoostMax*0.5,
				Cooperating:         rng.Float64() < 0.5, // Random start
				Source:              SourceInstitutional,
			}
		}
	}

	// Track results
	cooperationRates := make([]float64, params.NSteps)
	meanMotivations := make([]float64, params.NSteps)
	institutionalHealth := make([]float64, params.NSteps)
	cyclesTillCollapse := params.NSteps

	// Run simulation
	for step := 0; step < params.NSteps; step++ {
		// Calculate current cooperation rate
		coopCount := 0
		for i := range agents {
			if agents[i].Cooperating {
				coopCount++
			}
		}
		theta := float64(coopCount) / float64(params.NAgents)
		cooperationRates[step] = theta

		// Calculate mean motivation
		totalMot := 0.0
		for i := range agents {
			totalMot += agents[i].EffectiveMotivation
		}
		meanMotivations[step] = totalMot / float64(params.NAgents)

		// Institutional health = cooperation rate (simplified)
		instHealth := theta
		institutionalHealth[step] = instHealth

		// Check for collapse
		if theta < params.ThetaCrit && cyclesTillCollapse == params.NSteps {
			cyclesTillCollapse = step
		}

		// Apply exogenous shock if one occurs
		if params.ShockProbability > 0 && rng.Float64() < params.ShockProbability {
			// Shock hits institutional agents directly
			for i := range agents {
				if agents[i].Source == SourceInstitutional {
					// Shock reduces institutional boost AND forces defection
					// (simulates coordination failure, external crisis)
					agents[i].InstitutionalBoost *= (1 - params.ShockMagnitude)
					if rng.Float64() < params.ShockMagnitude {
						agents[i].Cooperating = false
					}
				}
				// Soteriological agents are unaffected by institutional shocks
			}
		}

		// Update each agent
		for i := range agents {
			// Update motivation based on source
			if agents[i].Source == SourceInstitutional {
				// Institutional motivation depends on institutional health
				if instHealth < params.CorruptionThreshold {
					// Institution degrading - boost decays
					agents[i].InstitutionalBoost *= (1 - params.InstitutionalDecayRate)
				} else {
					// Institution healthy - boost can grow (rate affected by scale)
					agents[i].InstitutionalBoost = math.Min(
						effectiveBoostMax,
						agents[i].InstitutionalBoost*(1+effectiveGrowthRate),
					)
				}
				agents[i].EffectiveMotivation = agents[i].BaseMotivation + agents[i].InstitutionalBoost

			} else {
				// Soteriological motivation - independent of institution
				// Can even increase under adversity (witness/martyrdom effect)
				if instHealth < params.CorruptionThreshold {
					// Adversity strengthens resolve (up to a point)
					adversityBoost := params.AdversityBoostRate * (params.CorruptionThreshold - instHealth)
					adversityBoost = math.Min(adversityBoost, params.MaxAdversityBoost)
					agents[i].EffectiveMotivation = agents[i].BaseMotivation + agents[i].SoteriologicalCore + adversityBoost
				} else {
					agents[i].EffectiveMotivation = agents[i].BaseMotivation + agents[i].SoteriologicalCore
				}
			}

			// Cooperation decision
			// Cooperate if M_i > c - β*θ - network_effect
			threshold := params.CooperationCost - params.BenefitMultiplier*theta
			// Network effects degraded by scale for institutional agents
			networkBoost := effectiveNetworkStr * theta
			if agents[i].Source == SourceSoteriological {
				// Soteriological agents maintain full network strength (shared values transcend scale)
				networkBoost = params.NetworkStrength * theta
			}
			effectiveMot := agents[i].EffectiveMotivation + networkBoost

			noise := rng.NormFloat64() * params.DecisionNoise
			agents[i].Cooperating = (effectiveMot + noise) > threshold
		}
	}

	// Final cooperation rate
	finalCoop := cooperationRates[params.NSteps-1]

	// Determine if cooperation is stable (above threshold for last 10%)
	stableWindow := params.NSteps / 10
	stable := true
	for i := params.NSteps - stableWindow; i < params.NSteps; i++ {
		if cooperationRates[i] < params.ThetaCrit {
			stable = false
			break
		}
	}

	return SimResult{
		CooperationRates:     cooperationRates,
		MeanMotivations:      meanMotivations,
		InstitutionalHealth:  institutionalHealth,
		FinalCooperationRate: finalCoop,
		StableCooperation:    stable,
		CyclesTillCollapse:   cyclesTillCollapse,
	}
}

// RunSimulations runs multiple simulations in parallel
func RunSimulations(params SimParams, nReps int, numWorkers int) []SimResult {
	results := make([]SimResult, nReps)

	var wg sync.WaitGroup
	chunkSize := nReps / numWorkers
	if chunkSize < 1 {
		chunkSize = 1
	}

	for w := 0; w < numWorkers; w++ {
		wg.Add(1)
		start := w * chunkSize
		end := start + chunkSize
		if w == numWorkers-1 {
			end = nReps
		}
		if start >= nReps {
			wg.Done()
			continue
		}

		go func(start, end int) {
			defer wg.Done()
			rng := rand.New(rand.NewSource(time.Now().UnixNano() + int64(start)))

			for i := start; i < end && i < nReps; i++ {
				results[i] = Simulate(params, rng)
			}
		}(start, end)
	}

	wg.Wait()
	return results
}

// Statistics for final cooperation rate
type Statistics struct {
	MeanCoopRate   float64 `json:"mean_coop_rate"`
	StdCoopRate    float64 `json:"std_coop_rate"`
	StableRate     float64 `json:"stable_rate"`
	MeanCollapse   float64 `json:"mean_collapse_cycle"`
}

func ComputeStatistics(results []SimResult) Statistics {
	n := len(results)
	if n == 0 {
		return Statistics{}
	}

	// Mean cooperation rate
	sum := 0.0
	stableCount := 0
	collapseSum := 0.0
	for _, r := range results {
		sum += r.FinalCooperationRate
		if r.StableCooperation {
			stableCount++
		}
		collapseSum += float64(r.CyclesTillCollapse)
	}
	mean := sum / float64(n)

	// Std
	sumSq := 0.0
	for _, r := range results {
		sumSq += (r.FinalCooperationRate - mean) * (r.FinalCooperationRate - mean)
	}
	std := math.Sqrt(sumSq / float64(n))

	return Statistics{
		MeanCoopRate: mean,
		StdCoopRate:  std,
		StableRate:   float64(stableCount) / float64(n),
		MeanCollapse: collapseSum / float64(n),
	}
}

func main() {
	// Command line flags
	nAgents := flag.Int("n", 1000, "Number of agents")
	nSteps := flag.Int("steps", 500, "Number of steps (time horizon)")
	nReps := flag.Int("reps", 50, "Number of replications")

	// Motivation sources
	soteriologicalFraction := flag.Float64("soterio-frac", 0.0, "Fraction with soteriological foundation")
	soteriologicalMean := flag.Float64("soterio-mean", 0.8, "Mean soteriological core motivation")

	// Institutional dynamics
	instDecay := flag.Float64("inst-decay", 0.05, "Institutional boost decay rate")
	instGrowth := flag.Float64("inst-growth", 0.02, "Institutional boost growth rate")
	corruptThreshold := flag.Float64("corrupt-threshold", 0.5, "Corruption threshold for decay")

	// Shock parameters
	shockProb := flag.Float64("shock-prob", 0.0, "Probability of shock each step")
	shockMag := flag.Float64("shock-mag", 0.5, "Shock magnitude (fraction of institutional boost lost)")

	// Cooperation dynamics
	coopCost := flag.Float64("cost", 1.0, "Cooperation cost")
	benefitMult := flag.Float64("benefit", 2.0, "Benefit multiplier from cooperation")
	networkStr := flag.Float64("network", 0.3, "Network strength")

	// Scale effects
	enableScale := flag.Bool("scale-effects", false, "Enable scale-dependent degradation")
	optimalScale := flag.Float64("optimal-scale", 150.0, "Dunbar-like optimal group size")
	scaleDecay := flag.Float64("scale-decay", 1.0, "Scale degradation rate")

	// Output
	jsonOutput := flag.String("json", "", "Output JSON file path")
	workers := flag.Int("workers", 0, "Number of workers (0 = NumCPU)")

	flag.Parse()

	if *workers == 0 {
		*workers = runtime.NumCPU()
	}

	params := SimParams{
		NAgents:                  *nAgents,
		NSteps:                   *nSteps,
		BaseMotivationMean:       0.3,
		BaseMotivationStd:        0.15,
		InstitutionalBoostMax:    0.8,
		InstitutionalDecayRate:   *instDecay,
		InstitutionalGrowthRate:  *instGrowth,
		CorruptionThreshold:      *corruptThreshold,
		SoteriologicalFraction:   *soteriologicalFraction,
		SoteriologicalCoreMean:   *soteriologicalMean,
		SoteriologicalCoreStd:    0.2,
		AdversityBoostRate:       0.5,
		MaxAdversityBoost:        0.3,
		CooperationCost:          *coopCost,
		BenefitMultiplier:        *benefitMult,
		NetworkStrength:          *networkStr,
		DecisionNoise:            0.1,
		ThetaCrit:                0.4,
		ShockProbability:         *shockProb,
		ShockMagnitude:           *shockMag,
		EnableScaleEffects:       *enableScale,
		OptimalScale:             *optimalScale,
		ScaleDecayRate:           *scaleDecay,
	}

	fmt.Printf("Running %d replications with %d workers...\n", *nReps, *workers)
	fmt.Printf("Agents: %d, Steps: %d\n", params.NAgents, params.NSteps)
	fmt.Printf("Soteriological fraction: %.0f%%\n", params.SoteriologicalFraction*100)
	fmt.Printf("Institutional decay: %.0f%%, growth: %.0f%%\n",
		params.InstitutionalDecayRate*100, params.InstitutionalGrowthRate*100)
	if params.ShockProbability > 0 {
		fmt.Printf("Shock probability: %.1f%%, magnitude: %.0f%%\n",
			params.ShockProbability*100, params.ShockMagnitude*100)
	}
	if params.EnableScaleEffects {
		scaleMult := scaleEffectMultiplier(params.NAgents, params.OptimalScale, params.ScaleDecayRate)
		fmt.Printf("Scale effects enabled: optimal=%.0f, decay=%.1f, multiplier=%.3f\n",
			params.OptimalScale, params.ScaleDecayRate, scaleMult)
	}

	start := time.Now()
	results := RunSimulations(params, *nReps, *workers)
	elapsed := time.Since(start)

	stats := ComputeStatistics(results)

	fmt.Printf("\nCompleted in %v\n", elapsed)
	fmt.Printf("\n=== Results ===\n")
	fmt.Printf("Final cooperation rate: %.1f%% (std: %.1f%%)\n", stats.MeanCoopRate*100, stats.StdCoopRate*100)
	fmt.Printf("Stable cooperation rate: %.1f%%\n", stats.StableRate*100)
	fmt.Printf("Mean cycles to collapse: %.0f\n", stats.MeanCollapse)

	// Output JSON if requested
	if *jsonOutput != "" {
		f, err := os.Create(*jsonOutput)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error creating JSON file: %v\n", err)
		} else {
			defer f.Close()
			enc := json.NewEncoder(f)
			enc.SetIndent("", "  ")
			enc.Encode(map[string]interface{}{
				"params": params,
				"stats":  stats,
			})
			fmt.Printf("Statistics written to %s\n", *jsonOutput)
		}
	}
}
