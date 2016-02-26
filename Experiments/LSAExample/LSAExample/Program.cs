using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using MathNet.Numerics.LinearAlgebra;

namespace LSAExample
{
    class Program
    {
        static void Main(string[] args)
        {
            var M = Matrix<double>.Build;
            /*double[,] x = { { 1, 0, 0, 1, 0, 0, 0, 0, 0 },
                            {1, 0, 1, 0, 0, 0, 0, 0, 0},
                            {1, 1, 0, 0, 0, 0, 0, 0, 0},
                            {0, 1, 1, 0, 1, 0, 0, 0, 0},
                            {0, 1, 1, 2, 0, 0, 0, 0, 0},
                            {0, 1, 0, 0, 1, 0, 0, 0, 0},
                            {0, 1, 0, 0, 1, 0, 0, 0, 0},
                            {0, 0, 1, 1, 0, 0, 0, 0, 0},
                            {0, 1, 0, 0, 0, 0, 0, 0, 1},
                            {0, 0, 0, 0, 0, 1, 1, 1, 0},
                            {0, 0, 0, 0, 0, 0, 1, 1, 1 },
                            { 0, 0, 0, 0, 0, 0, 0, 1, 1} };*/
            double[,] x = {{ 5f, 1f, 3f, 0f, 0f, 0f },
                           { 2f, 4f, 1f, 0f, 0f, 0f },
                           { 6f, 1f, 3f, 0f, 0f, 0f },
                           { 0f, 0f, 0f, 10f, 3f, 9f },
                           { 0f, 0f, 0f, 4f, 4f, 4f },};
            var A = M.DenseOfArray(x);
            Console.WriteLine(A);
            var svd = A.Svd(computeVectors: true);
            int k = 2;
            //Console.WriteLine(svd.U);
            //Console.WriteLine(svd.W);
            //Console.WriteLine(svd.VT);
            var Um = svd.U.SubMatrix(0, svd.U.ColumnCount, 0,k);
            //U.SetColumn(2, new double[5] { 0, 0, 0, 0, 0 });
            //U.SetColumn(3, new double[5] { 0, 0, 0, 0, 0 });
            //U.SetColumn(4, new double[5] { 0, 0, 0, 0, 0 });
            //var S = svd.S;
            //S[2] = 0;
            //S[3] = 0;
            //S[4] = 0;
            var VTm = svd.VT.SubMatrix(0, k, 0, svd.VT.RowCount);
            //VT.SetRow(2, new double[6] { 0, 0, 0, 0, 0, 0 });
            //VT.SetRow(3, new double[6] { 0, 0, 0, 0, 0, 0 });
            //VT.SetRow(4, new double[6] { 0, 0, 0, 0, 0, 0 });
            //VT.SetRow(5, new double[6] { 0, 0, 0, 0, 0, 0 });
            //var Sdiag = M.Diagonal(S.ToArray());
            var Wm = svd.W.SubMatrix(0, k, 0, k);
            //Console.WriteLine(A);
            //Console.WriteLine(Um);
            //Console.WriteLine(VTm.Transpose());
            //Console.WriteLine(Wm);
            //Console.WriteLine(S);
            //Console.WriteLine(Sdiag);
            //Console.WriteLine(svd.W);
            //var Ak = Um * Wm * VTm;
            Console.WriteLine(Um);
            Console.WriteLine(VTm.Transpose());


        }
    }
}
