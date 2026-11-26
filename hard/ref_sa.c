#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#define N 400
int n,m,f,init_[16],setup[16][16],fam[N],rel[N],due[N],w[N],proc[N][16],len[16],seq[16][N];long ct[16];int mk[16];
static unsigned long long S=88172645463325252ULL;static inline unsigned rnd(){S^=S<<13;S^=S>>7;S^=S<<17;return S>>11;}
static inline double ur(){return (rnd()&0xffffff)/16777216.0;}
long ev(int k,int*s,int l,int*M){long c=0;int t=0,g=init_[k];for(int i=0;i<l;i++){int x=s[i],u=setup[g][fam[x]];c+=3*u;t+=u;if(t<rel[x])t=rel[x];t+=proc[x][k];g=fam[x];if(t>due[x])c+=(long)w[x]*(t-due[x]);}*M=t;return c;}
int main(int a,char**v){double lim=atof(v[1]);S+=atoi(v[2])*1234567ULL;scanf("%d%d%d",&n,&m,&f);for(int i=0;i<m;i++)scanf("%d",&init_[i]);for(int i=0;i<f;i++)for(int j=0;j<f;j++)scanf("%d",&setup[i][j]);
for(int i=0;i<n;i++){scanf("%d%d%d%d",&fam[i],&rel[i],&due[i],&w[i]);for(int k=0;k<m;k++)scanf("%d",&proc[i][k]);}
int o[N];for(int i=0;i<n;i++)o[i]=i;for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)if(rel[o[j]]+due[o[j]]<rel[o[i]]+due[o[i]]){int t=o[i];o[i]=o[j];o[j]=t;}
for(int i=0;i<n;i++){int k=i%m;seq[k][len[k]++]=o[i];}for(int k=0;k<m;k++)ct[k]=ev(k,seq[k],len[k],&mk[k]);
long tot=0;int M=0;for(int k=0;k<m;k++){tot+=ct[k];if(mk[k]>M)M=mk[k];}long cur=tot+2*M,best=cur;double T0=300,T1=.4;clock_t t0=clock();double T=T0;long it=0;int A[N],Bb[N];
for(;;it++){if(!(it&255)){double p=(double)(clock()-t0)/CLOCKS_PER_SEC/lim;if(p>=1)break;T=T0*pow(T1/T0,p);}
int k1=rnd()%m,k2=rnd()%m;if(!len[k1])continue;int la,lb=0,i=rnd()%len[k1];
if(k1==k2){if(len[k1]<2)continue;int L=len[k1];for(int q=0;q<L;q++)A[q]=seq[k1][q];int j;if(rnd()&1){j=rnd()%L;int t=A[i];A[i]=A[j];A[j]=t;}else{int bl=1+rnd()%4;if(i+bl>L)bl=L-i;int tmp[8];for(int q=0;q<bl;q++)tmp[q]=A[i+q];for(int q=i;q+bl<L;q++)A[q]=A[q+bl];int R=L-bl;j=rnd()%(R+1);for(int q=R-1;q>=j;q--)A[q+bl]=A[q];for(int q=0;q<bl;q++)A[j+q]=tmp[q];}la=L;}
else if((rnd()&1)&&len[k2]){for(int q=0;q<len[k1];q++)A[q]=seq[k1][q];for(int q=0;q<len[k2];q++)Bb[q]=seq[k2][q];int j=rnd()%len[k2];int t=A[i];A[i]=Bb[j];Bb[j]=t;la=len[k1];lb=len[k2];}
else{int bl=1+rnd()%3;if(i+bl>len[k1])bl=len[k1]-i;int j=rnd()%(len[k2]+1);la=0;for(int q=0;q<len[k1];q++)if(q<i||q>=i+bl)A[la++]=seq[k1][q];lb=0;for(int q=0;q<j;q++)Bb[lb++]=seq[k2][q];for(int q=0;q<bl;q++)Bb[lb++]=seq[k1][i+q];for(int q=j;q<len[k2];q++)Bb[lb++]=seq[k2][q];}
int m1,m2=0;long c1=ev(k1,A,la,&m1),c2=0;if(k1!=k2)c2=ev(k2,Bb,lb,&m2);long nt=tot-ct[k1]+c1;if(k1!=k2)nt+=c2-ct[k2];int nM=m1;for(int k=0;k<m;k++){int x=k==k1?m1:(k==k2?m2:mk[k]);if(x>nM)nM=x;}long nc=nt+2*nM;
if(nc<=cur||ur()<exp((cur-nc)/T)){tot=nt;cur=nc;ct[k1]=c1;mk[k1]=m1;len[k1]=la;for(int q=0;q<la;q++)seq[k1][q]=A[q];if(k1!=k2){ct[k2]=c2;mk[k2]=m2;len[k2]=lb;for(int q=0;q<lb;q++)seq[k2][q]=Bb[q];}if(cur<best)best=cur;}}
printf("%ld %ld\n",best,it);}
