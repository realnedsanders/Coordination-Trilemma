/*
Monte Carlo Simulation of Corruption-TCS Cycle Dynamics

This simulates the trajectory described in Theorem 3.2 (Default Trajectory Terminus):
- S_C: Corruption phase (human enforcement)
- S_TCS_H: TCS with human controllers
- S_TCS_AI: TCS with autonomous AI control
- S_E: Extinction/enslavement (absorbing state)

Transition dynamics:
- S_C → S_TCS (with probability based on cycle dynamics)
- S_TCS_H → S_C (controllers corrupt, Theorem 2.1)
- S_TCS_AI → S_E (AI pursues own goals)

Key result: P(reach S_E) → 1 as number of cycles → ∞
*/

package main

import (
	"encoding/csv"
	"encoding/json"
	"flag"
	"fmt"
	"math"
	"math/rand"
	"os"
	"runtime"
	"sort"
	"sync"
	"time"
)

// State represents the system state
type State int

const (
	StateCorruption State = iota // S_C
	StateTCSHuman                // S_TCS_H
	StateTCSAI                   // S_TCS_AI
	StateExtinction              // S_E (absorbing)
)

func (s State) String() string {
	return [...]string{"Corruption", "TCS_Human", "TCS_AI", "Extinction"}[s]
}

// SimParams holds simulation parameters
type SimParams struct {
	// Probability of AI-controlled TCS when transitioning from corruption
	PAI float64 `json:"p_ai"`

	// Average cycle duration in years
	CycleDuration float64 `json:"cycle_duration"`

	// Standard deviation of cycle duration
	CycleDurationStd float64 `json:"cycle_duration_std"`

	// Probability that corruption leads to TCS (vs collapse and restart)
	PTCSTransition float64 `json:"p_tcs_transition"`

	// Rate at which p_ai increases per cycle (technological progress)
	PAIGrowthRate float64 `json:"p_ai_growth_rate"`

	// Maximum value for p_ai
	PAIMax float64 `json:"p_ai_max"`

	// Maximum simulation time in years
	MaxTime float64 `json:"max_time"`

	// Maximum number of cycles
	MaxCycles int `json:"max_cycles"`

	// Probability that AI alignment succeeds (AI-TCS doesn't lead to extinction)
	PAlignment float64 `json:"p_alignment"`
}

// SimResult holds the result of a single simulation
type SimResult struct {
	ReachedExtinction bool    `json:"reached_extinction"`
	TimeToExtinction  float64 `json:"time_to_extinction"`
	NumCycles         int     `json:"num_cycles"`
	FinalState        State   `json:"final_state"`
	FinalPAI          float64 `json:"final_p_ai"`
}

// Simulate runs a single trajectory
func Simulate(params SimParams, rng *rand.Rand) SimResult {
	state := StateCorruption
	currentTime := 0.0
	cycles := 0
	pAI := params.PAI

	for state != StateExtinction && currentTime < params.MaxTime && cycles < params.MaxCycles {
		cycles++

		// Sample cycle duration (log-normal for positive values)
		cycleDur := params.CycleDuration
		if params.CycleDurationStd > 0 {
			// Use normal approximation, ensure positive
			cycleDur = math.Max(1.0, rng.NormFloat64()*params.CycleDurationStd+params.CycleDuration)
		}

		switch state {
		case StateCorruption:
			// Corruption phase eventually leads to TCS or collapse
			if rng.Float64() < params.PTCSTransition {
				// Transition to TCS - human or AI controlled?
				if rng.Float64() < pAI {
					state = StateTCSAI
				} else {
					state = StateTCSHuman
				}
			}
			// else: collapse and restart corruption phase
			currentTime += cycleDur

		case StateTCSHuman:
			// Human controllers eventually corrupt (Theorem 2.1)
			// Return to corruption phase
			state = StateCorruption
			currentTime += cycleDur

		case StateTCSAI:
			// AI-controlled TCS - check if alignment succeeds
			if rng.Float64() < params.PAlignment {
				// Alignment succeeds - return to corruption phase
				// (AI system is controlled, but controllers eventually corrupt)
				state = StateCorruption
				currentTime += cycleDur
			} else {
				// Alignment fails - extinction/enslavement
				state = StateExtinction
				// No time added - immediate transition
			}
		}

		// p_ai increases over time (technological progress)
		pAI = math.Min(params.PAIMax, pAI*(1+params.PAIGrowthRate))
	}

	return SimResult{
		ReachedExtinction: state == StateExtinction,
		TimeToExtinction:  currentTime,
		NumCycles:         cycles,
		FinalState:        state,
		FinalPAI:          pAI,
	}
}

// RunSimulations runs n simulations in parallel
func RunSimulations(params SimParams, n int, numWorkers int) []SimResult {
	results := make([]SimResult, n)

	var wg sync.WaitGroup
	chunkSize := n / numWorkers

	for w := 0; w < numWorkers; w++ {
		wg.Add(1)
		start := w * chunkSize
		end := start + chunkSize
		if w == numWorkers-1 {
			end = n // Last worker takes remainder
		}

		go func(start, end int) {
			defer wg.Done()
			// Each goroutine gets its own RNG
			rng := rand.New(rand.NewSource(time.Now().UnixNano() + int64(start)))

			for i := start; i < end; i++ {
				results[i] = Simulate(params, rng)
			}
		}(start, end)
	}

	wg.Wait()
	return results
}

// Statistics holds summary statistics
type Statistics struct {
	N                    int     `json:"n"`
	ExtinctionRate       float64 `json:"extinction_rate"`
	MeanTime             float64 `json:"mean_time"`
	StdTime              float64 `json:"std_time"`
	MedianTime           float64 `json:"median_time"`
	P5Time               float64 `json:"p5_time"`
	P25Time              float64 `json:"p25_time"`
	P75Time              float64 `json:"p75_time"`
	P95Time              float64 `json:"p95_time"`
	MeanCycles           float64 `json:"mean_cycles"`
	MedianCycles         float64 `json:"median_cycles"`
}

// ComputeStatistics calculates summary statistics from results
func ComputeStatistics(results []SimResult) Statistics {
	n := len(results)
	if n == 0 {
		return Statistics{}
	}

	// Separate extinction times
	var extinctionTimes []float64
	var cycles []float64
	extinctionCount := 0

	for _, r := range results {
		if r.ReachedExtinction {
			extinctionTimes = append(extinctionTimes, r.TimeToExtinction)
			extinctionCount++
		}
		cycles = append(cycles, float64(r.NumCycles))
	}

	stats := Statistics{
		N:              n,
		ExtinctionRate: float64(extinctionCount) / float64(n),
	}

	// Time statistics (only for runs that reached extinction)
	if len(extinctionTimes) > 0 {
		sort.Float64s(extinctionTimes)

		// Mean
		sum := 0.0
		for _, t := range extinctionTimes {
			sum += t
		}
		stats.MeanTime = sum / float64(len(extinctionTimes))

		// Std
		sumSq := 0.0
		for _, t := range extinctionTimes {
			sumSq += (t - stats.MeanTime) * (t - stats.MeanTime)
		}
		stats.StdTime = math.Sqrt(sumSq / float64(len(extinctionTimes)))

		// Percentiles
		stats.MedianTime = percentile(extinctionTimes, 0.5)
		stats.P5Time = percentile(extinctionTimes, 0.05)
		stats.P25Time = percentile(extinctionTimes, 0.25)
		stats.P75Time = percentile(extinctionTimes, 0.75)
		stats.P95Time = percentile(extinctionTimes, 0.95)
	}

	// Cycle statistics
	if len(cycles) > 0 {
		sort.Float64s(cycles)
		sum := 0.0
		for _, c := range cycles {
			sum += c
		}
		stats.MeanCycles = sum / float64(len(cycles))
		stats.MedianCycles = percentile(cycles, 0.5)
	}

	return stats
}

func percentile(sorted []float64, p float64) float64 {
	if len(sorted) == 0 {
		return 0
	}
	idx := int(float64(len(sorted)-1) * p)
	return sorted[idx]
}

// WriteCSV writes results to CSV file
func WriteCSV(results []SimResult, filename string) error {
	f, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer f.Close()

	w := csv.NewWriter(f)
	defer w.Flush()

	// Header
	w.Write([]string{"reached_extinction", "time_to_extinction", "num_cycles", "final_state", "final_p_ai"})

	for _, r := range results {
		w.Write([]string{
			fmt.Sprintf("%t", r.ReachedExtinction),
			fmt.Sprintf("%.2f", r.TimeToExtinction),
			fmt.Sprintf("%d", r.NumCycles),
			r.FinalState.String(),
			fmt.Sprintf("%.4f", r.FinalPAI),
		})
	}

	return nil
}

func main() {
	// Command line flags
	nSims := flag.Int("n", 100000, "Number of simulations")
	pAI := flag.Float64("p-ai", 0.05, "Initial probability of AI-controlled TCS")
	cycleDur := flag.Float64("cycle", 50.0, "Average cycle duration in years")
	cycleStd := flag.Float64("cycle-std", 20.0, "Std dev of cycle duration")
	pTCS := flag.Float64("p-tcs", 0.8, "Probability corruption leads to TCS")
	growth := flag.Float64("growth", 0.1, "p_ai growth rate per cycle")
	maxTime := flag.Float64("max-time", 1000.0, "Maximum simulation time in years")
	maxCycles := flag.Int("max-cycles", 100, "Maximum number of cycles")
	pAlignment := flag.Float64("p-align", 0.0, "Probability AI alignment succeeds")
	output := flag.String("output", "", "Output CSV file path")
	jsonOutput := flag.String("json", "", "Output JSON stats file path")
	workers := flag.Int("workers", 0, "Number of workers (0 = NumCPU)")

	flag.Parse()

	if *workers == 0 {
		*workers = runtime.NumCPU()
	}

	params := SimParams{
		PAI:              *pAI,
		CycleDuration:    *cycleDur,
		CycleDurationStd: *cycleStd,
		PTCSTransition:   *pTCS,
		PAIGrowthRate:    *growth,
		PAIMax:           0.99,
		MaxTime:          *maxTime,
		MaxCycles:        *maxCycles,
		PAlignment:       *pAlignment,
	}

	fmt.Printf("Running %d simulations with %d workers...\n", *nSims, *workers)
	fmt.Printf("Parameters: p_ai=%.3f, cycle=%.1f±%.1f years, p_tcs=%.2f, growth=%.2f\n",
		params.PAI, params.CycleDuration, params.CycleDurationStd, params.PTCSTransition, params.PAIGrowthRate)

	start := time.Now()
	results := RunSimulations(params, *nSims, *workers)
	elapsed := time.Since(start)

	stats := ComputeStatistics(results)

	fmt.Printf("\nCompleted in %v\n", elapsed)
	fmt.Printf("\n=== Results ===\n")
	fmt.Printf("Extinction rate: %.2f%%\n", stats.ExtinctionRate*100)
	fmt.Printf("Time to extinction:\n")
	fmt.Printf("  Mean: %.1f years (std: %.1f)\n", stats.MeanTime, stats.StdTime)
	fmt.Printf("  Median: %.1f years\n", stats.MedianTime)
	fmt.Printf("  5th percentile: %.1f years\n", stats.P5Time)
	fmt.Printf("  25th percentile: %.1f years\n", stats.P25Time)
	fmt.Printf("  75th percentile: %.1f years\n", stats.P75Time)
	fmt.Printf("  95th percentile: %.1f years\n", stats.P95Time)
	fmt.Printf("Cycles to extinction:\n")
	fmt.Printf("  Mean: %.1f cycles\n", stats.MeanCycles)
	fmt.Printf("  Median: %.1f cycles\n", stats.MedianCycles)

	// Write outputs
	if *output != "" {
		if err := WriteCSV(results, *output); err != nil {
			fmt.Fprintf(os.Stderr, "Error writing CSV: %v\n", err)
		} else {
			fmt.Printf("\nResults written to %s\n", *output)
		}
	}

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
