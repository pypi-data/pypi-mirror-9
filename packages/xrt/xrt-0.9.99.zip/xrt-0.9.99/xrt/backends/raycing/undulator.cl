//__author__ = "Konstantin Klementiev, Roman Chernikov"
//__date__ = "10 Apr 2015"

//#pragma OPENCL EXTENSION cl_khr_fp64: enable

__kernel void undulator(const float alpha,
                    const float Kx,
                    const float Ky,
                    const float phase,
                    const int jend,
                    __global float* gamma,
                    __global float* wu,
                    __global float* w, 
                    __global float* ww1,
                    __global float* ddphi,
                    __global float* ddpsi,
                    __global float* tg, 
                    __global float* ag,
                    __global float2* Is_gl,
                    __global float2* Ip_gl)
{
        unsigned int ii = get_global_id(0);
        int j;

        float2 beta;
        float2 eucos;
        float ucos;
        float2 zero2 = (float2)(0,0);
        float2 Is = zero2;
        float2 Ip = zero2;
        float wgwu = w[ii] / gamma[ii] / wu[ii];
        float Kx2 = Kx * Kx;
        float Ky2 = Ky * Ky;
        for(j=0; j<jend; j++)
          {
            ucos = (double)(ww1[ii]) * tg[j] + wgwu *
               (-Ky * ddphi[ii] * (sin(tg[j])) +
                Kx * ddpsi[ii] * sin(tg[j] + phase) +
                0.125 / gamma[ii] * (Ky2 * sin(2. * tg[j]) +
                Kx2 * sin(2. * (tg[j] + phase))));

            eucos.x = cos(ucos);
            eucos.y = sin(ucos);

            beta.x = -Ky / gamma[ii] * cos(tg[j]);
            beta.y = Kx / gamma[ii] * cos(tg[j] + phase);

            Is += (ag[j] * (ddphi[ii] + beta.x)) * eucos;
            Ip += (ag[j] * (ddpsi[ii] + beta.y)) * eucos;

          }
        mem_fence(CLK_LOCAL_MEM_FENCE);
        Is_gl[ii] = Is;
        Ip_gl[ii] = Ip;
}

__kernel void undulator_taper(const float alpha,
                    const float Kx,
                    const float Ky,
                    const float phase,
                    const int jend,
                    __global float* gamma,
                    __global float* wu,
                    __global float* w, 
                    __global float* ww1,
                    __global float* ddtheta,
                    __global float* ddpsi,
                    __global float* tg, 
                    __global float* ag,
                    __global float2* Is_gl,
                    __global float2* Ip_gl)
{
        const float E2W = 1.51926751475e15;
        const float C = 2.99792458e11;
        unsigned int ii = get_global_id(0);
        int j;

        float2 eucos, beta;
        float ucos, sintg, sin2tg, costg;
        float2 zero2 = (float2)(0,0);
        float2 Is = zero2;
        float2 Ip = zero2;
        float Kx2 = Kx * Kx;
        float Ky2 = Ky * Ky;
        float alphaS = alpha * C / wu[ii] / E2W;
        float wgwu = w[ii] / gamma[ii] / wu[ii];
        for(j=0; j<jend; j++)
          {
            sintg = sin(tg[j]);
            sin2tg = sin(2 * tg[j]);
            costg = cos(tg[j]);
            ucos = ww1[ii] * tg[j] + wgwu *
                (-Ky * ddtheta[ii] *(sintg + alphaS *
                                      (1 - costg - tg[j] * sintg)) +
                  Kx * ddpsi[ii] * sin(tg[j] + phase) + 
                  0.125 / gamma[ii] * 
                  (Ky2 * (sin2tg - 2 * alphaS *
                    (tg[j] * tg[j] + costg * costg + tg[j] * sin2tg)) +
                   Kx2 * sin(2. * (tg[j] + phase))));

            eucos.x = cos(ucos);
            eucos.y = sin(ucos);

            beta.x = -Ky / gamma[ii] * costg;
            beta.y = Kx / gamma[ii] * cos(tg[j] + phase);

            Is += ag[j] * (ddtheta[ii] + beta.x *
                (1 - alphaS * tg[j])) * eucos;
            Ip += ag[j] * (ddpsi[ii] + beta.y) * eucos;
          }
        mem_fence(CLK_LOCAL_MEM_FENCE);
        Is_gl[ii] = Is;
        Ip_gl[ii] = Ip;
}

__kernel void undulator_nf(const float R0,
                    const float Kx,
                    const float Ky,
                    const float phase,
                    const int jend,
                    __global float* gamma,
                    __global float* wu,
                    __global float* w, 
                    __global float* ddphi,
                    __global float* ddpsi,
                    __global float* tg, 
                    __global float* ag,
                    __global float2* Is_gl,
                    __global float2* Ip_gl)
{
        const float E2W = 1.51926751475e15;
        const float C = 2.99792458e11;

        unsigned int ii = get_global_id(0);
        int j;

        float2 eucos;
        float ucos;
        float2 zero2 = (float2)(0,0);
        float2 Is = zero2;
        float2 Ip = zero2;
        float3 r, r0;
        float2 beta;
        float Kx2 = Kx * Kx;
        float Ky2 = Ky * Ky;        
        float gamma2 = gamma[ii] * gamma[ii];
        float betam = 1 - (1 + 0.5 * Kx2 + 0.5 * Ky2) / 2. / gamma2;

        float wR0 = R0 / C * E2W;
        r0.x = wR0 * tan(-ddphi[ii]);
        r0.y = wR0 * tan(ddpsi[ii]);
        r0.z = wR0 * cos(sqrt(ddphi[ii]*ddphi[ii] + ddpsi[ii]*ddpsi[ii]));

        for(j=0; j<jend; j++)
          {

          r.x = Ky / wu[ii] / gamma[ii] * sin(tg[j]);
          r.y = -Kx / wu[ii] / gamma[ii] * sin(tg[j] + phase);
          r.z = betam * tg[j] / wu[ii] - 0.125 / wu[ii] / gamma2 *
                (Ky2 * sin(2 * tg[j]) + Kx2 * sin(2 * (tg[j] + phase)));

          ucos = w[ii] * (tg[j] / wu[ii] + length(r0 - r));

          eucos.x = cos(ucos);
          eucos.y = sin(ucos);

          beta.x = -Ky / gamma[ii] * cos(tg[j]);
          beta.y = Kx / gamma[ii] * cos(tg[j] + phase);

          Is += ag[j] * (-ddphi[ii] + beta.x) * eucos;
          Ip += ag[j] * (ddpsi[ii] + beta.y) * eucos;
          }
        mem_fence(CLK_LOCAL_MEM_FENCE);

        Is_gl[ii] = Is;
        Ip_gl[ii] = Ip;
}