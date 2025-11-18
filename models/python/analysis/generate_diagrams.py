"""
Generate conceptual diagrams for the Coordination Trilemma paper.

This script creates:
1. Coordination Trilemma 3D trade-off diagram
2. Default Trajectory state machine
3. Scale degradation curves (four mechanisms)
"""

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


def create_trilemma_diagram(output_path: str = None):
    """
    Create a 3D diagram showing the Coordination Trilemma trade-offs.

    The three vertices represent:
    - Scale (large population coordination)
    - Voluntary participation
    - Effective coordination

    The trilemma shows that achieving all three simultaneously is impossible
    without soteriological motivation.
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Define triangle vertices in 3D space
    vertices = np.array([
        [0, 0, 1],      # Scale (top)
        [1, 0, 0],      # Voluntary (right)
        [-0.5, 0.866, 0]  # Effective (left)
    ])

    # Draw triangle edges
    for i in range(3):
        j = (i + 1) % 3
        ax.plot3D([vertices[i, 0], vertices[j, 0]],
                  [vertices[i, 1], vertices[j, 1]],
                  [vertices[i, 2], vertices[j, 2]],
                  'b-', linewidth=2)

    # Fill triangle
    tri = Poly3DCollection([vertices], alpha=0.3, facecolor='lightblue', edgecolor='blue')
    ax.add_collection3d(tri)

    # Label vertices
    labels = ['Scale\n(N > 10^6)', 'Voluntary\nParticipation', 'Effective\nCoordination']
    offsets = [(0.05, -0.05, 0.1), (0.1, -0.05, -0.05), (-0.2, 0.1, -0.05)]

    for i, (label, offset) in enumerate(zip(labels, offsets)):
        ax.text(vertices[i, 0] + offset[0],
                vertices[i, 1] + offset[1],
                vertices[i, 2] + offset[2],
                label, fontsize=11, fontweight='bold', ha='center')

    # Mark impossible region (center of triangle)
    center = vertices.mean(axis=0)
    ax.scatter([center[0]], [center[1]], [center[2]],
               c='red', s=200, marker='x', linewidths=3)
    ax.text(center[0], center[1] + 0.15, center[2] - 0.1,
            'Impossible\nwithout M_i',
            fontsize=10, ha='center', color='darkred')

    # Mark achievable pairs on edges
    edge_labels = [
        ('Scale +\nVoluntary', (0.5, 0, 0.5), 'Coordination fails'),
        ('Voluntary +\nEffective', (0.25, 0.433, 0), 'Small scale only'),
        ('Scale +\nEffective', (-0.25, 0.433, 0.5), 'Coercion required')
    ]

    for label, pos, sublabel in edge_labels:
        ax.text(pos[0], pos[1], pos[2], f'{label}\n({sublabel})',
                fontsize=8, ha='center', style='italic', alpha=0.8)

    # Set view angle
    ax.view_init(elev=20, azim=45)

    # Remove axes for cleaner look
    ax.set_axis_off()

    # Title
    plt.title('Coordination Trilemma: Trade-offs in Large-Scale Coordination',
              fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved trilemma diagram to {output_path}")
    else:
        plt.show()

    plt.close()


def create_state_machine_diagram(output_path: str = None):
    """
    Create a state machine diagram showing the Default Trajectory.

    States:
    - S_C: Corruption phase
    - S_TCS_H: TCS with human controllers
    - S_TCS_AI: TCS with AI control
    - S_E: Extinction (absorbing)
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    # State positions
    states = {
        'S_C': (0.2, 0.5),
        'S_TCS_H': (0.5, 0.8),
        'S_TCS_AI': (0.5, 0.2),
        'S_E': (0.85, 0.5)
    }

    # State labels and descriptions
    state_labels = {
        'S_C': ('Corruption\nPhase', 'Human enforcement\ncorrupts over time'),
        'S_TCS_H': ('TCS\n(Human)', 'Human controllers\nof TCS'),
        'S_TCS_AI': ('TCS\n(AI)', 'Autonomous AI\ncontrol'),
        'S_E': ('Extinction', 'Absorbing state')
    }

    # Draw states
    for state, (x, y) in states.items():
        if state == 'S_E':
            # Absorbing state - double circle
            circle1 = plt.Circle((x, y), 0.08, fill=False, color='darkred', linewidth=3)
            circle2 = plt.Circle((x, y), 0.065, fill=False, color='darkred', linewidth=2)
            ax.add_patch(circle1)
            ax.add_patch(circle2)
            color = 'darkred'
        elif state == 'S_C':
            circle = plt.Circle((x, y), 0.08, fill=True, facecolor='lightyellow',
                               edgecolor='orange', linewidth=2)
            ax.add_patch(circle)
            color = 'darkorange'
        else:
            circle = plt.Circle((x, y), 0.08, fill=True, facecolor='lightblue',
                               edgecolor='blue', linewidth=2)
            ax.add_patch(circle)
            color = 'darkblue'

        label, desc = state_labels[state]
        ax.text(x, y + 0.01, label, ha='center', va='center',
                fontsize=10, fontweight='bold', color=color)
        ax.text(x, y - 0.14, desc, ha='center', va='top',
                fontsize=8, style='italic', color='gray')

    # Draw transitions
    transitions = [
        ('S_C', 'S_TCS_H', 'P_TCS(1-P_AI)', 'above'),
        ('S_C', 'S_TCS_AI', 'P_TCS * P_AI', 'below'),
        ('S_TCS_H', 'S_C', 'P=1\n(Thm 2.1)', 'above'),
        ('S_TCS_AI', 'S_E', '1-P_align', 'below'),
        ('S_TCS_AI', 'S_C', 'P_align', 'above'),
    ]

    for start, end, label, pos in transitions:
        x1, y1 = states[start]
        x2, y2 = states[end]

        # Adjust for circle radius
        dx, dy = x2 - x1, y2 - y1
        dist = np.sqrt(dx**2 + dy**2)

        # Arrow start/end adjusted for circle radius
        rad = 0.085
        x1_adj = x1 + rad * dx / dist
        y1_adj = y1 + rad * dy / dist
        x2_adj = x2 - rad * dx / dist
        y2_adj = y2 - rad * dy / dist

        # Curve the arrow slightly
        if start == 'S_TCS_H' and end == 'S_C':
            connectionstyle = "arc3,rad=0.3"
        elif start == 'S_TCS_AI' and end == 'S_C':
            connectionstyle = "arc3,rad=-0.3"
        else:
            connectionstyle = "arc3,rad=0.1"

        arrow = FancyArrowPatch((x1_adj, y1_adj), (x2_adj, y2_adj),
                                connectionstyle=connectionstyle,
                                arrowstyle='-|>', mutation_scale=15,
                                color='gray', linewidth=1.5)
        ax.add_patch(arrow)

        # Label position
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        offset = 0.05 if pos == 'above' else -0.05

        ax.text(mid_x, mid_y + offset, label, ha='center', va='center',
                fontsize=8, bbox=dict(boxstyle='round,pad=0.3',
                                     facecolor='white', alpha=0.8))

    # Self-loop for S_C (collapse and restart)
    x, y = states['S_C']
    loop = mpatches.FancyArrowPatch((x - 0.08, y), (x - 0.08, y - 0.001),
                                    connectionstyle="arc3,rad=-2",
                                    arrowstyle='-|>', mutation_scale=12,
                                    color='gray', linewidth=1.5)
    ax.add_patch(loop)
    ax.text(x - 0.15, y - 0.08, '1-P_TCS\n(restart)', ha='center', fontsize=7)

    # Title and annotations
    ax.set_title('Default Trajectory State Machine\n(Theorem 3.2)',
                 fontsize=14, fontweight='bold')

    # Key insight box
    ax.text(0.5, -0.05,
            'Key: P(reach S_E) → 1 as cycles → ∞',
            ha='center', fontsize=10, style='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))

    ax.set_xlim(0, 1)
    ax.set_ylim(-0.1, 1)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved state machine diagram to {output_path}")
    else:
        plt.show()

    plt.close()


def create_scale_degradation_curves(output_path: str = None):
    """
    Create curves showing the four mechanisms of institutional degradation with scale.

    Mechanisms:
    1. Monitoring effectiveness
    2. Reputation reliability
    3. Social pressure
    4. Free-rider detection
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Scale range
    N = np.linspace(150, 10000, 1000)
    optimal_scale = 150

    # Mechanism 1: Monitoring effectiveness
    ax = axes[0, 0]
    monitoring = np.minimum(1.0, optimal_scale / N)
    ax.plot(N, monitoring, 'b-', linewidth=2)
    ax.axvline(x=optimal_scale, color='green', linestyle='--', alpha=0.5, label='Dunbar limit')
    ax.axhline(y=0.5, color='red', linestyle=':', alpha=0.5)
    ax.set_xlabel('Population Scale (N)')
    ax.set_ylabel('Effectiveness')
    ax.set_title('Monitoring Effectiveness\nmin(1, optimal/N)', fontweight='bold')
    ax.set_xlim(0, 10000)
    ax.set_ylim(0, 1.1)
    ax.fill_between(N, monitoring, alpha=0.3)
    ax.text(5000, 0.1, f'At N=1000: {optimal_scale/1000:.1%}', fontsize=9)
    ax.legend(loc='upper right')

    # Mechanism 2: Reputation reliability
    ax = axes[0, 1]
    chain_length = np.log(N / optimal_scale) / np.log(2)
    chain_length = np.maximum(0, chain_length)
    reputation = np.power(0.9, chain_length)
    ax.plot(N, reputation, 'g-', linewidth=2)
    ax.axvline(x=optimal_scale, color='green', linestyle='--', alpha=0.5)
    ax.set_xlabel('Population Scale (N)')
    ax.set_ylabel('Reliability')
    ax.set_title('Reputation Reliability\n(0.9)^chain_length', fontweight='bold')
    ax.set_xlim(0, 10000)
    ax.set_ylim(0, 1.1)
    ax.fill_between(N, reputation, alpha=0.3, color='green')
    ax.text(5000, 0.3, f'At N=1000: {0.9**np.log2(1000/150):.1%}', fontsize=9)

    # Mechanism 3: Social pressure
    ax = axes[1, 0]
    pressure = np.minimum(1.0, optimal_scale / N)
    ax.plot(N, pressure, 'orange', linewidth=2)
    ax.axvline(x=optimal_scale, color='green', linestyle='--', alpha=0.5)
    ax.set_xlabel('Population Scale (N)')
    ax.set_ylabel('Pressure')
    ax.set_title('Social Pressure Diffusion\noptimal/N', fontweight='bold')
    ax.set_xlim(0, 10000)
    ax.set_ylim(0, 1.1)
    ax.fill_between(N, pressure, alpha=0.3, color='orange')
    ax.text(5000, 0.3, 'Strangers << close relations', fontsize=9, style='italic')

    # Mechanism 4: Free-rider detection
    ax = axes[1, 1]
    detection = optimal_scale / N
    ax.plot(N, detection, 'r-', linewidth=2)
    ax.axvline(x=optimal_scale, color='green', linestyle='--', alpha=0.5)
    ax.set_xlabel('Population Scale (N)')
    ax.set_ylabel('Detection Probability')
    ax.set_title('Free-rider Detection\noptimal/N', fontweight='bold')
    ax.set_xlim(0, 10000)
    ax.set_ylim(0, 1.1)
    ax.fill_between(N, detection, alpha=0.3, color='red')
    ax.text(5000, 0.3, f'At N=1000: {optimal_scale/1000:.1%}', fontsize=9)

    # Combined effect plot as inset
    fig.text(0.5, 0.02,
             'Combined Institutional Effectiveness = (Monitor × Reputation × Pressure × Detection)^0.25\n'
             'At N=1000: ≈22%  |  At N=10000: ≈4%',
             ha='center', fontsize=10, style='italic',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))

    plt.suptitle('Scale-Dependent Institutional Degradation\nFour Explicit Mechanisms',
                 fontsize=14, fontweight='bold', y=1.02)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved scale degradation curves to {output_path}")
    else:
        plt.show()

    plt.close()


def create_enforcement_regress_flowchart(output_path: str = None):
    """
    Create a flowchart showing the enforcement regress problem.

    Shows: Who enforces the enforcers? → Infinite regress or corruption
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    # Define boxes
    boxes = [
        (0.15, 0.85, 'Population\n(N agents)', 'lightblue'),
        (0.15, 0.65, 'Primary\nEnforcers', 'lightyellow'),
        (0.15, 0.45, 'Secondary\nEnforcers', 'lightyellow'),
        (0.15, 0.25, 'Tertiary\nEnforcers', 'lightyellow'),
        (0.15, 0.05, '...', 'white'),
    ]

    # Draw boxes
    for x, y, label, color in boxes:
        rect = FancyBboxPatch((x, y), 0.2, 0.12, boxstyle='round,pad=0.01',
                              facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x + 0.1, y + 0.06, label, ha='center', va='center',
                fontsize=10, fontweight='bold')

    # Draw arrows between levels
    for i in range(4):
        y_start = boxes[i][1]
        y_end = boxes[i + 1][1] + 0.12
        ax.annotate('', xy=(0.25, y_end), xytext=(0.25, y_start),
                    arrowprops=dict(arrowstyle='->', color='gray', lw=2))
        ax.text(0.38, (y_start + y_end) / 2, 'enforces', ha='left', va='center',
                fontsize=9, style='italic')

    # Problem annotation on right side
    ax.text(0.6, 0.7, 'The Regress Problem:', fontsize=12, fontweight='bold')
    problems = [
        '• Each level requires enforcement',
        '• Cannot add infinite levels',
        '• Top level is unmonitored',
        '• Result: Top corrupts first',
        '• Corruption cascades down'
    ]
    for i, prob in enumerate(problems):
        ax.text(0.6, 0.6 - i * 0.08, prob, fontsize=10)

    # Show corruption cascade
    ax.annotate('', xy=(0.35, 0.25), xytext=(0.35, 0.65),
                arrowprops=dict(arrowstyle='->', color='red', lw=3,
                               connectionstyle='arc3,rad=0.3'))
    ax.text(0.42, 0.45, 'Corruption\ncascade', ha='left', va='center',
            fontsize=10, color='darkred', fontweight='bold')

    # Solutions comparison
    ax.text(0.6, 0.25, 'Attempted Solutions:', fontsize=11, fontweight='bold')
    ax.text(0.6, 0.18, '✗ More levels → Infinite regress', fontsize=9, color='darkred')
    ax.text(0.6, 0.12, '✗ External monitoring → Who monitors them?', fontsize=9, color='darkred')
    ax.text(0.6, 0.06, '✓ Intrinsic motivation (M_i) → No external enforcement needed',
            fontsize=9, color='darkgreen')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.title('Enforcement Regress: Why Hierarchical Enforcement Fails',
              fontsize=14, fontweight='bold')
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved enforcement regress flowchart to {output_path}")
    else:
        plt.show()

    plt.close()


def create_detection_timeline(output_path: str = None):
    """
    Create a timeline showing synthetic media detection arms race.
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    # Timeline data
    events = [
        (2017, 'Deepfakes emerge', 'gen', 'First face-swap videos'),
        (2018, 'Basic detection', 'det', 'Blink detection works'),
        (2019, 'GAN improvements', 'gen', 'StyleGAN, realistic blinks'),
        (2020, 'Neural detection', 'det', 'Deep learning classifiers'),
        (2021, 'Voice cloning', 'gen', 'Real-time voice synthesis'),
        (2022, 'Diffusion models', 'gen', 'Stable Diffusion, DALL-E'),
        (2023, 'Multimodal detection', 'det', 'Cross-modal consistency checks'),
        (2024, 'Video generation', 'gen', 'Sora, consistent video'),
        (2025, 'Detection lag', 'det', '~6 month lag typical'),
        (2026, '?', 'gen', 'Real-time indistinguishable?'),
    ]

    # Draw timeline
    ax.axhline(y=0.5, color='black', linewidth=2, zorder=1)

    # Plot events
    for year, label, etype, desc in events:
        if etype == 'gen':
            y = 0.7
            color = 'red'
            marker = 'v'
        else:
            y = 0.3
            color = 'blue'
            marker = '^'

        ax.scatter(year, y, s=150, c=color, marker=marker, zorder=3)
        ax.plot([year, year], [0.5, y], color=color, linestyle='--', alpha=0.5, zorder=2)
        ax.text(year, y + 0.08 if etype == 'gen' else y - 0.08,
                label, ha='center', va='bottom' if etype == 'gen' else 'top',
                fontsize=9, fontweight='bold', rotation=30)
        ax.text(year, y + 0.18 if etype == 'gen' else y - 0.18,
                desc, ha='center', va='bottom' if etype == 'gen' else 'top',
                fontsize=7, style='italic', alpha=0.8, rotation=30)

    # Labels
    ax.text(2016.5, 0.75, 'Generation\nAdvances', fontsize=10, color='darkred',
            fontweight='bold', va='center')
    ax.text(2016.5, 0.25, 'Detection\nMethods', fontsize=10, color='darkblue',
            fontweight='bold', va='center')

    # Key insight
    ax.text(2021.5, 0.05,
            'Key Insight: Detection consistently lags generation by 6-12 months.\n'
            'Eventually, synthetic media becomes computationally indistinguishable.',
            ha='center', fontsize=10, style='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.9))

    ax.set_xlim(2016, 2027)
    ax.set_ylim(0, 1)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_xticks(range(2017, 2027))
    ax.set_yticks([])

    plt.title('Synthetic Media Arms Race: Generation vs Detection',
              fontsize=14, fontweight='bold')
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved detection timeline to {output_path}")
    else:
        plt.show()

    plt.close()


def create_longevity_scatter(output_path: str = None):
    """
    Create a scatter plot of historical system longevity vs scale.
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Historical data (estimated)
    systems = [
        ('Roman Empire', 70e6, 503, 'red'),
        ('Han Dynasty', 55e6, 426, 'orange'),
        ('Byzantine Empire', 26e6, 1123, 'purple'),
        ('Ming Dynasty', 160e6, 276, 'green'),
        ('Mongol Empire', 100e6, 162, 'brown'),
        ('British India', 400e6, 190, 'blue'),
        ('Soviet Union', 290e6, 69, 'darkred'),
        ('Ottoman Empire', 35e6, 624, 'teal'),
        ('Maurya Empire', 50e6, 137, 'olive'),
        ('Umayyad Caliphate', 62e6, 89, 'coral'),
    ]

    for name, pop, years, color in systems:
        ax.scatter(pop / 1e6, years, s=200, c=color, alpha=0.7, edgecolors='black', linewidth=1)
        ax.annotate(name, (pop / 1e6, years), xytext=(5, 5),
                    textcoords='offset points', fontsize=9)

    # Trend line (negative correlation)
    pops = [s[1] / 1e6 for s in systems]
    years = [s[2] for s in systems]
    z = np.polyfit(np.log10(pops), years, 1)
    p = np.poly1d(z)
    x_line = np.linspace(20, 450, 100)
    ax.plot(x_line, p(np.log10(x_line)), 'k--', alpha=0.5, label='Trend')

    # Annotations
    ax.axhline(y=250, color='red', linestyle=':', alpha=0.3)
    ax.text(350, 260, 'Median ~250 years', fontsize=9, color='darkred')

    ax.set_xlabel('Peak Population (millions)', fontsize=12)
    ax.set_ylabel('System Longevity (years)', fontsize=12)
    ax.set_xscale('log')

    # Key finding
    ax.text(0.5, 0.02,
            'Larger scale → Shorter longevity\n'
            'Correlation consistent with scale-dependent institutional degradation',
            transform=ax.transAxes, ha='center', fontsize=10, style='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.9))

    plt.title('Historical Coordination Systems: Scale vs Longevity',
              fontsize=14, fontweight='bold')
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved longevity scatter plot to {output_path}")
    else:
        plt.show()

    plt.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate conceptual diagrams")
    parser.add_argument("--output", type=str, default=None, help="Output directory")
    parser.add_argument("--all", action="store_true", help="Generate all diagrams")
    parser.add_argument("--tier1", action="store_true", help="Generate Tier 1 diagrams")
    parser.add_argument("--tier2", action="store_true", help="Generate Tier 2 diagrams")
    parser.add_argument("--trilemma", action="store_true", help="Generate trilemma diagram")
    parser.add_argument("--state-machine", action="store_true", help="Generate state machine")
    parser.add_argument("--degradation", action="store_true", help="Generate degradation curves")
    parser.add_argument("--regress", action="store_true", help="Generate enforcement regress")
    parser.add_argument("--timeline", action="store_true", help="Generate detection timeline")
    parser.add_argument("--longevity", action="store_true", help="Generate longevity scatter")

    args = parser.parse_args()

    # Set defaults
    if args.all:
        args.tier1 = args.tier2 = True
    if args.tier1:
        args.trilemma = args.state_machine = args.degradation = True
    if args.tier2:
        args.regress = args.timeline = args.longevity = True

    # If nothing specified, do all
    if not any([args.trilemma, args.state_machine, args.degradation,
                args.regress, args.timeline, args.longevity]):
        args.trilemma = args.state_machine = args.degradation = True
        args.regress = args.timeline = args.longevity = True

    if args.trilemma:
        path = f"{args.output}/coordination_trilemma.png" if args.output else None
        create_trilemma_diagram(path)

    if args.state_machine:
        path = f"{args.output}/default_trajectory_state_machine.png" if args.output else None
        create_state_machine_diagram(path)

    if args.degradation:
        path = f"{args.output}/scale_degradation_curves.png" if args.output else None
        create_scale_degradation_curves(path)

    if args.regress:
        path = f"{args.output}/enforcement_regress.png" if args.output else None
        create_enforcement_regress_flowchart(path)

    if args.timeline:
        path = f"{args.output}/detection_timeline.png" if args.output else None
        create_detection_timeline(path)

    if args.longevity:
        path = f"{args.output}/longevity_scatter.png" if args.output else None
        create_longevity_scatter(path)

    print("Done generating diagrams!")
