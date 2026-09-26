from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent / 'outputs' / 'equations'
OUT.mkdir(parents=True, exist_ok=True)

expressions = {
    'centreline_parameter': r'$x_i(s)$',
    'parameter_interval': r'$s\in[0,1]$',
    'piecewise_points': r'$x_{i,0},\ldots,x_{i,m}$',
    'graph': r'$G=(V,E)$',
    'incidence_space': r'$\mathbb{R}^{M\times N}$',
    'slenderness': r'$r_i/L_i\ll1$',
    'conductance': r'$g_i=1/R_i$',
    'radius_sensitivity': r'$1/0.8^4=2.44$',
    'concentration': r'$C/C_0$',
    'radius_power': r'$r_i^{-4}$',
    'property_bundle': r'$L_i,\ r_i,\ R_i,\ Q_i,\ u_i;\ P_j,\ x_j$',
    'rho': r'$\rho$',
    'mu': r'$\mu$',
    'r_squared': r'$R^2=1.00$',
    'nodal_vector': r'$p=[P_1,\ldots,P_N]^T$',
    'bp': r'$Bp$',
    'diag_conductance': r'$G=\operatorname{diag}(g_1,\ldots,g_M)$',
    'lambda': r'$\lambda$',
    'q_i': r'$Q_i$',
    'l_i': r'$L_i$',
    'r_i': r'$r_i$',
    'r_cap_i': r'$R_i$',
    'u_i': r'$u_i$',
    'p_j': r'$P_j$',
    'x_j': r'$x_j$',
    'p_j_minus_p_k': r'$P_j-P_k$',
}

for name, expr in expressions.items():
    fig = plt.figure(figsize=(max(1.4, len(expr) * 0.12), 0.42), dpi=240)
    fig.text(0.02, 0.5, expr, fontsize=15, va='center', ha='left', color='black')
    fig.patch.set_alpha(0)
    fig.savefig(OUT / f'{name}.png', transparent=True, bbox_inches='tight', pad_inches=0.02)
    plt.close(fig)
print(f'wrote {len(expressions)} rendered inline equations to {OUT}')
