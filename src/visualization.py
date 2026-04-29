import matplotlib.pyplot as plt
import seaborn as sns

def plot_conversion_rate(control_rate, treatment_rate):
    """
    Plot conversion rates for control and treatment groups.
    """
    groups = ['Control (A)', 'Treatment (B)']
    rates = [control_rate, treatment_rate]
    plt.bar(groups, rates, color=['blue', 'green'])
    plt.title('Conversion Rate by Group')
    plt.ylabel('Conversion Rate')
    plt.show()

def plot_ltv(control_ltv, treatment_ltv):
    """
    Plot average LTV for control and treatment groups.
    """
    groups = ['Control (A)', 'Treatment (B)']
    ltv_values = [control_ltv, treatment_ltv]
    plt.bar(groups, ltv_values, color=['blue', 'green'])
    plt.title('Average LTV by Group')
    plt.ylabel('LTV (USD)')
    plt.show()
