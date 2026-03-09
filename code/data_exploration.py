import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def run_advanced_eda(file_path="data/bank_churn.csv"):
    """
    Performs Advanced Exploratory Data Analysis on the bank churn dataset.
    """
    df = pd.read_csv(file_path)
    # Drop non-predictive columns for visualization
    df_plot = df.drop(['RowNumber', 'CustomerId', 'Surname'], axis=1)
    
    print("--- Dataset Shape ---")
    print(df.shape)
    
    # 1. Target Imbalance Analysis
    plt.figure(figsize=(8, 5))
    df['Exited'].value_counts(normalize=True).plot(kind='bar', color=['skyblue', 'salmon'])
    plt.title('Churn Proportion (0: Stayed, 1: Exited)')
    plt.ylabel('Percentage')
    plt.savefig('data/target_imbalance.png')
    plt.close()
    
    # 2. Categorical Analysis: Impact on Churn
    categorical_features = ['Geography', 'Gender', 'HasCrCard', 'IsActiveMember', 'NumOfProducts']
    fig, axes = plt.subplots(3, 2, figsize=(15, 18))
    axes = axes.flatten()
    
    for i, feature in enumerate(categorical_features):
        sns.countplot(x=feature, hue='Exited', data=df, ax=axes[i], palette='muted')
        axes[i].set_title(f'Churn by {feature}')
        axes[i].legend(title='Exited', loc='upper right')
        
    plt.tight_layout()
    plt.savefig('data/categorical_impact.png')
    plt.close()
    
    # 3. Numerical Analysis: Outlier Detection using Boxplots
    numerical_features = ['CreditScore', 'Age', 'Tenure', 'Balance', 'EstimatedSalary']
    plt.figure(figsize=(15, 10))
    for i, feature in enumerate(numerical_features):
        plt.subplot(2, 3, i+1)
        sns.boxplot(y=df[feature], x=df['Exited'], palette='Set2')
        plt.title(f'{feature} Distribution by Churn')
    
    plt.tight_layout()
    plt.savefig('data/numerical_boxplots.png')
    plt.close()
    
    # 4. Multivariate Analysis: Pairplot (Sampled for performance)
    sns.pairplot(df_plot.sample(1000), hue='Exited', diag_kind='kde', palette='husl')
    plt.savefig('data/multivariate_pairplot.png')
    plt.close()
    
    # 5. Correlation Heatmap (Focusing on Target)
    plt.figure(figsize=(10, 8))
    corr = df_plot.corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
    plt.title('Feature Correlation Heatmap')
    plt.savefig('data/correlation_heatmap_v2.png')
    plt.close()

    print("\nAdvanced EDA completed. New plots saved in 'data/' directory.")

if __name__ == "__main__":
    run_advanced_eda()