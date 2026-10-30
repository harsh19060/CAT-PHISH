from pathlib import Path
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.data_loader import load_dataset

root=Path(__file__).resolve().parents[1]
X,y,_=load_dataset()
corr=X.copy(); corr['target_phishing']=y
matrix=corr.corr(method='pearson')
fig,ax=plt.subplots(figsize=(14,12))
sns.heatmap(matrix,annot=True,fmt='.2f',cmap='coolwarm',center=0,vmin=-1,vmax=1,
            square=True,linewidths=.35,ax=ax,annot_kws={'size':5.3},
            cbar_kws={'label':'Pearson correlation'})
ax.set_title('URL-only features and target (1 = phishing)',fontsize=13,pad=12)
ax.tick_params(axis='x',labelrotation=70,labelsize=7)
ax.tick_params(axis='y',labelrotation=0,labelsize=7)
fig.tight_layout()
fig.savefig(root/'reports'/'feature_target_correlation.png',dpi=210,bbox_inches='tight')
plt.close(fig)
target=matrix['target_phishing'].drop('target_phishing').abs().sort_values(ascending=False)
print('Top absolute correlations:',target.head(5).to_dict())
