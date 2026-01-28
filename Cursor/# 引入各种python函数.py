import seaborn as sns
import matplotlib.pyplot as plt

# 加载示例数据集
tips = sns.load_dataset("tips")

# 利用seaborn创建表格（热力图展示tips数据的相关性）
corr = tips.corr(numeric_only=True)
sns.heatmap(corr, annot=True, cmap="YlGnBu")

plt.title("Tips数据集数值特征相关性表格")
plt.show()


