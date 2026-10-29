// Reproducible, lossless 2D quasi-static cross-section estimate, not a USB compliance solver.
// Compile: clang++ -O3 -std=c++17 scripts/usb_cross_section_fd.cpp -o /private/tmp/usb_fd
// Args: pitch_mm half_box_width_mm box_height_mm case_name Er_pp Er_core trace_width gap
// Cases: in2, in2_coplanar, in2_b_ground, in2_b_ground_coplanar, front, single_in2, single_front.
// Half-domain odd-mode symmetry (x=0,V=0), positive trace V=1. Differential voltage=2V.
// Uniform finite-volume grid, harmonic dielectric interfaces, PCG, conductor charge by Gauss flux.
// Codd=Q/V; vacuum solve gives Codd0; Zdiff=2/(c*sqrt(Codd*Codd0)).
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>
using namespace std;
struct Result { double c; int iterations; double residual; int nx,ny; };
Result solve(double d,double xmax,double ymax,string mode,double pp,double core,double w,double gap,bool vacuum,double bhalf){
 const int nx=ceil(xmax/d),ny=ceil(ymax/d),N=nx*ny; const bool front=mode=="front"||mode=="single_front",single=mode.find("single_")==0,plate=mode=="parallel_plate";
 const bool bg=mode.find("b_ground")!=string::npos,cp=mode.find("coplanar")!=string::npos;
 const double h=front?.2104:.4000,t=front?.035:.0152,top=front?h+t:.4000+.0152+.2104;
 const double left=single?1.0:gap/2,right=left+w; // single trace away from symmetry; full box must be >=3mm.
 vector<double> er(N),v(N),diag(N),rhs(N),r(N),p(N),z(N),ap(N),kx(N),ky(N);
 vector<unsigned char> fixed(N); vector<int> freeids,signal;
 for(int j=0;j<ny;j++)for(int i=0;i<nx;i++){
  const int a=j*nx+i;const double x=(i+.5)*d,y=(j+.5)*d;
  const double masktop=front&&x>=left&&x<right?h+t+.01524:h+.03048;
  er[a]=vacuum?1:(plate?core:(front?(y<h?pp:(y<masktop?3.8:1)):(y<h?core:(y<top?pp:(y<top+.03048?3.8:1)))));
  if((plate&&y>=h)||(y>=h&&y<h+t&&x>=left&&x<right)){fixed[a]=2;v[a]=1;signal.push_back(a);}
  else if((bg&&y>=top&&y<top+.035&&x<bhalf)||(cp&&y>=h&&y<h+t&&x>=right+.15)){fixed[a]=1;}
 }
 auto hm=[](double a,double b){return 2*a*b/(a+b);};
 for(int j=0;j<ny;j++)for(int i=0;i<nx;i++){
  const int a=j*nx+i;auto ec=[&](int b){if(fixed[a]&&!fixed[b])return 2*er[b];if(!fixed[a]&&fixed[b])return 2*er[a];return hm(er[a],er[b]);};
  if(i<nx-1)kx[a]=ec(a+1);if(j<ny-1)ky[a]=ec(a+nx);
 }
 for(int j=0;j<ny;j++)for(int i=0;i<nx;i++){
  int a=j*nx+i;if(fixed[a])continue;freeids.push_back(a);
  auto edge=[&](int b,double k){diag[a]+=k;if(fixed[b])rhs[a]+=k*v[b];};
  if(i)edge(a-1,kx[a-1]);else if(!plate)diag[a]+=2*er[a];
  if(i<nx-1)edge(a+1,kx[a]);else if(!plate)diag[a]+=2*er[a];
  if(j)edge(a-nx,ky[a-nx]);else diag[a]+=2*er[a];
  if(j<ny-1)edge(a+nx,ky[a]);else diag[a]+=2*er[a];
 }
 auto mult=[&](const vector<double>&q,vector<double>&o){for(int a:freeids){int i=a%nx,j=a/nx;double val=diag[a]*q[a];
  if(i&&!fixed[a-1])val-=kx[a-1]*q[a-1];if(i<nx-1&&!fixed[a+1])val-=kx[a]*q[a+1];
  if(j&&!fixed[a-nx])val-=ky[a-nx]*q[a-nx];if(j<ny-1&&!fixed[a+nx])val-=ky[a]*q[a+nx];o[a]=val;}};
 double rz=0,rhsnorm=0;for(int a:freeids){r[a]=rhs[a];z[a]=r[a]/diag[a];p[a]=z[a];rz+=r[a]*z[a];rhsnorm+=r[a]*r[a];}
 int it=0;double residual=1;
 for(;it<12000;it++){
  mult(p,ap);double pap=0;for(int a:freeids)pap+=p[a]*ap[a];double alpha=rz/pap,rr=0;
  for(int a:freeids){v[a]+=alpha*p[a];r[a]-=alpha*ap[a];rr+=r[a]*r[a];}
  residual=sqrt(rr/rhsnorm);if(residual<1e-9)break;
  double next=0;for(int a:freeids){z[a]=r[a]/diag[a];next+=r[a]*z[a];}double beta=next/rz;for(int a:freeids)p[a]=z[a]+beta*p[a];rz=next;
 }
 double q=0;for(int a:signal){int i=a%nx,j=a/nx;if(i&&! (fixed[a-1]==2))q+=kx[a-1]*(1-v[a-1]);if(i<nx-1&&fixed[a+1]!=2)q+=kx[a]*(1-v[a+1]);if(j&&fixed[a-nx]!=2)q+=ky[a-nx]*(1-v[a-nx]);if(j<ny-1&&fixed[a+nx]!=2)q+=ky[a]*(1-v[a+nx]);}
 return{q*8.8541878128e-12,it,residual,nx,ny};
}
int main(int argc,char**argv){if(argc!=9&&argc!=10){cerr<<"pitch half_width height mode Er_pp Er_core width gap [B_ground_half_width]\n";return 1;}
 double d=atof(argv[1]),x=atof(argv[2]),y=atof(argv[3]),pp=atof(argv[5]),core=atof(argv[6]),w=atof(argv[7]),gap=atof(argv[8]);string mode=argv[4];
 double bhalf=argc==10?atof(argv[9]):x;
 auto a=solve(d,x,y,mode,pp,core,w,gap,false,bhalf),b=solve(d,x,y,mode,pp,core,w,gap,true,bhalf);bool single=mode.find("single_")==0||mode=="parallel_plate";
 cout<<setprecision(12)<<"{\"mode\":\""<<mode<<"\",\"pitch_mm\":"<<d<<",\"half_box_width_mm\":"<<x<<",\"box_height_mm\":"<<y<<",\"b_ground_half_width_mm\":"<<bhalf<<",\"er_pp\":"<<pp<<",\"er_core\":"<<core<<",\"width_mm\":"<<w<<",\"gap_mm\":"<<gap<<",\"C_odd_F_per_m\":"<<a.c<<",\"C_odd_vacuum_F_per_m\":"<<b.c<<",\"Z_"<<(single?"single":"diff")<<"_ohm\":"<<(single?1:2)/(299792458*sqrt(a.c*b.c))<<",\"iterations\":["<<a.iterations<<","<<b.iterations<<"],\"relative_residual\":["<<a.residual<<","<<b.residual<<"],\"nx\":"<<a.nx<<",\"ny\":"<<a.ny<<"}\n";
}
