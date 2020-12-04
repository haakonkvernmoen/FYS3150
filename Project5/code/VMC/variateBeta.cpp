#include "variationalMC.hpp"
#include "trialFunctions.cpp"

int main(int argc, char *argv[]) {
	int searches = 2;
	double omega = 1;
	int MCCs = (int)pow(10,6);

	double maxAlpha = 1.1;
	double minAlpha = 0.8;
	int N_alpha = 20;
	double dAlpha;

	double minBeta = 0;
	double maxBeta = 1;
	int N_beta = 20;
	double dBeta;
	

	double bestAlpha = 0.9; // Here use best value from wavefunc1 with Coulomb interaction
	double alpha;

	double bestBeta;
	double beta;

	double Energy_min = 100; // Just a big number to get started
	double Energy;

	double step;

	for(int i = 0; i < searches; i++) {
		dAlpha = (maxAlpha - minAlpha)/(double)(N_alpha-1);
		dBeta = (maxBeta - minBeta)/(double)(N_beta-1);

		
		step = 1.5/sqrt(bestAlpha);

		cout << "BETA" <<endl;
		for(int j = 0; j < N_beta; j++) {
			beta = minBeta + j*dBeta;
			VMC* problem = new VMC(psi_T2, EL_2, MCCs, step, omega, bestAlpha, beta);
			problem->Run_NoSave();

			Energy = problem->getEnergy();
			cout << "E = " << Energy << " beta = " << beta << " alpha = " << bestAlpha << endl;
			if(Energy < Energy_min) {
				Energy_min = Energy;
				bestBeta = beta;
			}

			delete problem;
		}
	
		cout << "ALPHA" <<endl;
		for(int j = 0; j < N_alpha; j++) {
			alpha = minAlpha + j*dAlpha;
			VMC* problem = new VMC(psi_T2, EL_2, MCCs, step, omega, alpha, bestBeta);
			problem->Run_NoSave();

			Energy = problem->getEnergy();
			cout << "E = " << Energy << " beta = " << bestBeta << " alpha = " << alpha << endl;

			if(Energy < Energy_min) {
				Energy_min = Energy;
				bestAlpha = alpha;
			}

			delete problem;
		}
	}

	cout << "Beep-Boop im done found lowest energy E = " << Energy 
	<< " at alpha = " << bestAlpha << " beta = " << bestBeta << endl;
}