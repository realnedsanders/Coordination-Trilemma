/*
Polycentric Governance Model (Ostrom's Design Principles) - Go Implementation

Tests whether Ostrom's design principles can break corruption inevitability,
with proper modeling of scale-dependent degradation.

Scale effects modeled:
1. Peer monitoring effectiveness decreases with group size
2. Social pressure diffuses with group size
3. Collective-choice costs increase with group size

Key insight: Ostrom's principles may be equivalent to VCS (Voluntary Cooperation System)
fundamentals - we test this by examining which mechanisms are load-bearing.
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

// Participant represents an agent in the governance system
type Participant struct {
	Integrity        float64
	BaseIntegrity    float64
	Corrupt          bool
	GroupID          int
	SanctionsReceived int
}

// SimParams holds simulation parameters
type SimParams struct {
	NParticipants int     `json:"n_participants"`
	NGroups       int     `json:"n_groups"`
	NSteps        int     `json:"n_steps"`

	// Ostrom principles toggles
	OstromMonitoring   bool `json:"ostrom_monitoring"`
	GraduatedSanctions bool `json:"graduated_sanctions"`
	CollectiveChoice   bool `json:"collective_choice"`

	// Scale effect parameters
	ScaleEffects           bool    `json:"scale_effects"`
	MonitoringDecayRate    float64 `json:"monitoring_decay_rate"`    // How fast monitoring degrades with group size
	SocialPressureDecay    float64 `json:"social_pressure_decay"`    // How fast social pressure diffuses
	OptimalGroupSize       float64 `json:"optimal_group_size"`       // Group size at which effects start degrading

	// Base parameters
	BaseDetectionProb    float64 `json:"base_detection_prob"`
	VigilanceFactor      float64 `json:"vigilance_factor"`
	SanctionBase         float64 `json:"sanction_base"`
	SocialPressureFactor float64 `json:"social_pressure_factor"`
	CorruptionGain       float64 `json:"corruption_gain"`
	StakeFactor          float64 `json:"stake_factor"`
	IntegrityWeight      float64 `json:"integrity_weight"`
	IntegrityMean        float64 `json:"integrity_mean"`
	IntegrityStd         float64 `json:"integrity_std"`
	IntegrityDecayRate   float64 `json:"integrity_decay_rate"`
	IntegrityRecoveryRate float64 `json:"integrity_recovery_rate"`
}

// SimResult holds results from a single simulation
type SimResult struct {
	FinalCorruptionRate float64 `json:"final_corruption_rate"`
	FinalMeanIntegrity  float64 `json:"final_mean_integrity"`
}

// getGroupCorruptionRate calculates corruption rate for a specific group
func getGroupCorruptionRate(participants []Participant, groupID int) float64 {
	count := 0
	corrupt := 0
	for i := range participants {
		if participants[i].GroupID == groupID {
			count++
			if participants[i].Corrupt {
				corrupt++
			}
		}
	}
	if count == 0 {
		return 0.0
	}
	return float64(corrupt) / float64(count)
}

// getGroupSize returns number of participants in a group
func getGroupSize(participants []Participant, groupID int) int {
	count := 0
	for i := range participants {
		if participants[i].GroupID == groupID {
			count++
		}
	}
	return count
}

// scaleEffectMultiplier calculates degradation based on group size
// Returns 1.0 at optimal size, decreasing as size increases
func scaleEffectMultiplier(groupSize int, optimalSize, decayRate float64) float64 {
	if float64(groupSize) <= optimalSize {
		return 1.0
	}
	// Exponential decay beyond optimal size
	excess := float64(groupSize) - optimalSize
	return math.Exp(-decayRate * excess / optimalSize)
}

// Simulate runs a single simulation
func Simulate(params SimParams, rng *rand.Rand) SimResult {
	// Initialize participants
	participants := make([]Participant, params.NParticipants)
	for i := range participants {
		integrity := math.Max(0.1, rng.NormFloat64()*params.IntegrityStd+params.IntegrityMean)
		participants[i] = Participant{
			Integrity:     integrity,
			BaseIntegrity: integrity,
			Corrupt:       false,
			GroupID:       i % params.NGroups,
			SanctionsReceived: 0,
		}
	}

	// Run simulation
	for step := 0; step < params.NSteps; step++ {
		// Shuffle order for fairness
		perm := rng.Perm(params.NParticipants)

		for _, idx := range perm {
			p := &participants[idx]
			groupCorruption := getGroupCorruptionRate(participants, p.GroupID)
			groupSize := getGroupSize(participants, p.GroupID)

			if p.Corrupt {
				// Consider reform (only with graduated sanctions)
				if params.GraduatedSanctions {
					groupCooperation := 1.0 - groupCorruption

					// Social pressure from honest peers
					socialPressure := params.SocialPressureFactor * groupCooperation

					// Apply scale effect to social pressure
					if params.ScaleEffects {
						socialPressure *= scaleEffectMultiplier(groupSize, params.OptimalGroupSize, params.SocialPressureDecay)
					}

					// Diminishing returns to continued corruption
					continuedGain := params.CorruptionGain * math.Pow(0.9, float64(p.SanctionsReceived))

					// Recovery of integrity
					integrityRecovery := p.BaseIntegrity * 0.1

					// Decision to reform
					reformBenefit := socialPressure + integrityRecovery
					reformCost := continuedGain

					if reformBenefit > reformCost+rng.NormFloat64()*0.1 {
						p.Corrupt = false
						p.SanctionsReceived = int(math.Max(0, float64(p.SanctionsReceived-1)))
					}
				}

				// Integrity decay if still corrupt
				if p.Corrupt {
					p.Integrity *= (1 - params.IntegrityDecayRate)
					p.SanctionsReceived++
				}
			} else {
				// Consider corruption
				var detectionProb float64

				if params.OstromMonitoring {
					// Peer monitoring: detection stays high or increases
					detectionProb = params.BaseDetectionProb + params.VigilanceFactor*groupCorruption

					// Apply scale effect - monitoring degrades with group size
					if params.ScaleEffects {
						detectionProb *= scaleEffectMultiplier(groupSize, params.OptimalGroupSize, params.MonitoringDecayRate)
					}

					detectionProb = math.Min(0.95, detectionProb)
				} else {
					// Hierarchical: detection decreases with corruption
					detectionProb = params.BaseDetectionProb * (1 - groupCorruption)
				}

				// Expected penalty
				var expectedPenalty float64
				if params.GraduatedSanctions {
					expectedPenalty = params.SanctionBase * (1 + float64(p.SanctionsReceived))
				} else {
					expectedPenalty = params.SanctionBase * 5
				}

				// Integrity cost
				integrityCost := p.Integrity * params.IntegrityWeight

				// Collective-choice stake
				var stakeCost float64
				if params.CollectiveChoice {
					stakeCost = params.StakeFactor * (1 - groupCorruption)

					// Apply scale effect - stake diffuses with group size
					if params.ScaleEffects {
						stakeCost *= scaleEffectMultiplier(groupSize, params.OptimalGroupSize, params.SocialPressureDecay)
					}
				}

				// Decision
				expectedBenefit := params.CorruptionGain
				expectedCost := detectionProb*expectedPenalty + integrityCost + stakeCost

				if expectedBenefit+rng.NormFloat64()*0.1 > expectedCost {
					p.Corrupt = true
				} else {
					// Stayed honest - potential integrity recovery
					if params.GraduatedSanctions {
						recovery := (p.BaseIntegrity - p.Integrity) * params.IntegrityRecoveryRate
						p.Integrity = math.Min(p.BaseIntegrity, p.Integrity+recovery)
					}
				}
			}
		}
	}

	// Calculate final results
	corruptCount := 0
	totalIntegrity := 0.0
	for i := range participants {
		if participants[i].Corrupt {
			corruptCount++
		}
		totalIntegrity += participants[i].Integrity
	}

	return SimResult{
		FinalCorruptionRate: float64(corruptCount) / float64(params.NParticipants),
		FinalMeanIntegrity:  totalIntegrity / float64(params.NParticipants),
	}
}

// RunSimulations runs multiple simulations in parallel
func RunSimulations(params SimParams, nReps int, numWorkers int) []SimResult {
	results := make([]SimResult, nReps)

	var wg sync.WaitGroup
	chunkSize := nReps / numWorkers

	for w := 0; w < numWorkers; w++ {
		wg.Add(1)
		start := w * chunkSize
		end := start + chunkSize
		if w == numWorkers-1 {
			end = nReps
		}

		go func(start, end int) {
			defer wg.Done()
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
	Mean float64 `json:"mean"`
	Std  float64 `json:"std"`
}

// ComputeStatistics calculates mean and std of corruption rates
func ComputeStatistics(results []SimResult) Statistics {
	n := len(results)
	if n == 0 {
		return Statistics{}
	}

	// Mean
	sum := 0.0
	for _, r := range results {
		sum += r.FinalCorruptionRate
	}
	mean := sum / float64(n)

	// Std
	sumSq := 0.0
	for _, r := range results {
		sumSq += (r.FinalCorruptionRate - mean) * (r.FinalCorruptionRate - mean)
	}
	std := math.Sqrt(sumSq / float64(n))

	return Statistics{Mean: mean, Std: std}
}

func main() {
	// Command line flags
	nParticipants := flag.Int("n", 100, "Number of participants")
	nGroups := flag.Int("groups", 5, "Number of groups")
	nSteps := flag.Int("steps", 200, "Number of steps")
	nReps := flag.Int("reps", 10, "Number of replications")

	// Ostrom toggles
	ostromMonitoring := flag.Bool("ostrom-monitoring", true, "Enable peer monitoring")
	graduatedSanctions := flag.Bool("graduated-sanctions", true, "Enable graduated sanctions")
	collectiveChoice := flag.Bool("collective-choice", true, "Enable collective choice")

	// Scale effects
	scaleEffects := flag.Bool("scale-effects", true, "Enable scale-dependent degradation")
	monitoringDecay := flag.Float64("monitoring-decay", 0.5, "Monitoring decay rate with group size")
	socialDecay := flag.Float64("social-decay", 0.3, "Social pressure decay rate")
	optimalGroupSize := flag.Float64("optimal-size", 20.0, "Optimal group size (Dunbar-ish)")

	// Output
	jsonOutput := flag.String("json", "", "Output JSON file path")
	workers := flag.Int("workers", 0, "Number of workers (0 = NumCPU)")

	flag.Parse()

	if *workers == 0 {
		*workers = runtime.NumCPU()
	}

	params := SimParams{
		NParticipants:          *nParticipants,
		NGroups:                *nGroups,
		NSteps:                 *nSteps,
		OstromMonitoring:       *ostromMonitoring,
		GraduatedSanctions:     *graduatedSanctions,
		CollectiveChoice:       *collectiveChoice,
		ScaleEffects:           *scaleEffects,
		MonitoringDecayRate:    *monitoringDecay,
		SocialPressureDecay:    *socialDecay,
		OptimalGroupSize:       *optimalGroupSize,
		BaseDetectionProb:      0.2,
		VigilanceFactor:        0.4,
		SanctionBase:           0.5,
		SocialPressureFactor:   0.3,
		CorruptionGain:         2.0,
		StakeFactor:            0.2,
		IntegrityWeight:        0.1,
		IntegrityMean:          5.0,
		IntegrityStd:           1.0,
		IntegrityDecayRate:     0.05,
		IntegrityRecoveryRate:  0.1,
	}

	groupSize := params.NParticipants / params.NGroups

	fmt.Printf("Running %d replications with %d workers...\n", *nReps, *workers)
	fmt.Printf("Participants: %d, Groups: %d, Group size: %d\n", params.NParticipants, params.NGroups, groupSize)
	fmt.Printf("Ostrom: monitoring=%v, sanctions=%v, choice=%v\n",
		params.OstromMonitoring, params.GraduatedSanctions, params.CollectiveChoice)
	if params.ScaleEffects {
		fmt.Printf("Scale effects: optimal_size=%.0f, monitoring_decay=%.2f, social_decay=%.2f\n",
			params.OptimalGroupSize, params.MonitoringDecayRate, params.SocialPressureDecay)
	}

	start := time.Now()
	results := RunSimulations(params, *nReps, *workers)
	elapsed := time.Since(start)

	stats := ComputeStatistics(results)

	fmt.Printf("\nCompleted in %v\n", elapsed)
	fmt.Printf("\n=== Results ===\n")
	fmt.Printf("Corruption rate: %.1f%% (std: %.1f%%)\n", stats.Mean*100, stats.Std*100)

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
