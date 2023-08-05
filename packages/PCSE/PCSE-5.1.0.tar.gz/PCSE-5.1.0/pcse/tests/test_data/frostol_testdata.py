#!/usr/bin/env python

headers = "DAY;LT50T;LT50C;TEMP_CROWN;snow_depth;LT50I;FROSTOL_H;RH;FROSTOL_D;RDH_TEMP;FROSTOL_S;RDH_TSTR;FROSTOL_R;resp;Fsnow;RDH_RESP;VR;VD;fV" 
raw_data = [
    "1;-4.01;-24;10;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;0.9999;0;0.0000;0.7393;0.0000;0.0000",
    "2;-4.01;-24;10;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;0.9999;0;0.0000;0.7393;0.7393;0.0000",
    "3;-4.01;-24;10;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;0.9999;0;0.0000;0.7393;1.4786;0.0000",
    "4;-4.01;-24;13.27;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.3751;0;0.0000;0.3618;2.2179;0.0000",
    "5;-4.01;-24;13.27;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.3751;0;0.0000;0.3618;2.5798;0.0000",
    "6;-4.01;-24;13.27;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.3751;0;0.0000;0.3618;2.9416;0.0000",
    "7;-4.01;-24;13.27;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.3751;0;0.0000;0.3618;3.3034;0.0001",
    "8;-4.01;-24;14.93;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.5908;0;0.0000;0.1215;3.6653;0.0001",
    "9;-4.01;-24;14.22;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.4963;0;0.0000;0.2280;3.7868;0.0001",
    "10;-4.01;-24;13.78;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.4395;0;0.0000;0.2912;4.0147;0.0002",
    "11;-4.01;-24;14.42;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.5226;0;0.0000;0.1985;4.3059;0.0003",
    "12;-4.01;-24;14.41;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.5213;0;0.0000;0.2000;4.5045;0.0003",
    "13;-4.01;-24;14.13;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.4846;0;0.0000;0.2411;4.7045;0.0004",
    "14;-4.01;-24;13.27;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.3751;0;0.0000;0.3618;4.9455;0.0005",
    "15;-4.01;-24;13.09;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.3528;0;0.0000;0.3860;5.3074;0.0007",
    "16;-4.01;-24;13.22;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.3689;0;0.0000;0.3686;5.6934;0.0010",
    "17;-4.01;-24;13.58;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.4140;0;0.0000;0.3193;6.0620;0.0014",
    "18;-4.01;-24;11.03;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.1114;0;0.0000;0.6353;6.3813;0.0018",
    "19;-4.01;-24;10.11;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.0115;0;0.0000;0.7289;7.0166;0.0029",
    "20;-4.01;-24;10.77;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.0827;0;0.0000;0.6629;7.7455;0.0048",
    "21;-4.01;-24;12.28;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;0;0.54;1.2549;0;0.0000;0.4903;8.4084;0.0072",
    "22;-4.01;-24;9.84;0;-4.01;0.0093;0.0297;0.000027;0.0000;1.9;0;0.54;0.9831;0;0.0000;0.7541;8.8987;0.0096",
    "23;-4.04;-24;6.72;0;-4.01;0.0093;0.6089;0.000027;0.0000;1.9;0;0.54;0.6810;0;0.0000;0.9626;9.6529;0.0143",
    "24;-4.65;-24;8.53;0;-4.01;0.0093;0.2646;0.000027;0.0000;1.9;0;0.54;0.8504;0;0.0000;0.8612;10.6154;0.0228",
    "25;-4.91;-24;9.53;0;-4.01;0.0093;0.0834;0.000027;0.0000;1.9;0;0.54;0.9509;0;0.0000;0.7818;11.4766;0.0334",
    "26;-4.99;-24;7.52;0;-4.01;0.0093;0.4383;0.000027;0.0000;1.9;0;0.54;0.7540;0;0.0000;0.9249;12.2584;0.0458",
    "27;-5.43;-24;6.28;0;-4.01;0.0093;0.6423;0.000027;0.0000;1.9;0;0.54;0.6421;0;0.0000;0.9781;13.1833;0.0646",
    "28;-6.08;-24;8.06;0;-4.01;0.0093;0.3234;0.000027;0.0000;1.9;0;0.54;0.8049;0;0.0000;0.8930;14.1614;0.0899",
    "29;-6.40;-24;9.03;0;-4.01;0.0093;0.1588;0.000027;0.0000;1.9;0;0.54;0.9000;0;0.0000;0.8234;15.0543;0.1182",
    "30;-6.56;-24;7.57;0;-4.01;0.0093;0.3942;0.000027;0.0000;1.9;0;0.54;0.7586;0;0.0000;0.9221;15.8777;0.1489",
    "31;-6.95;-24;4.7;0;-4.01;0.0093;0.8403;0.000027;0.0000;1.9;0;0.54;0.5094;0;0.0000;0.9995;16.7999;0.1884",
    "32;-7.79;-24;5.6;0;-4.01;0.0093;0.6632;0.000027;0.0000;1.9;0;0.54;0.5837;0;0.0000;0.9942;17.7994;0.2365",
    "33;-8.46;-24;6.29;0;-4.01;0.0093;0.5363;0.000027;0.0000;1.9;0;0.54;0.6430;0;0.0000;0.9778;18.7936;0.2890",
    "34;-8.99;-24;8.14;0;-4.01;0.0093;0.2596;0.000027;0.0000;1.9;0;0.54;0.8126;0;0.0000;0.8878;19.7713;0.3438",
    "35;-9.25;-24;7.79;0;-4.01;0.0093;0.3031;0.000027;0.0000;1.9;0;0.54;0.7793;0;0.0000;0.9096;20.6591;0.3949",
    "36;-9.55;-24;8.88;0;-4.01;0.0093;0.1505;0.000027;0.0000;1.9;0;0.54;0.8850;0;0.0000;0.8351;21.5687;0.4474",
    "37;-9.70;-24;6.77;0;-4.01;0.0093;0.4294;0.000027;0.0000;1.9;0;0.54;0.6855;0;0.0000;0.9606;22.4038;0.4946",
    "38;-10.13;-24;6.31;0;-4.01;0.0093;0.4758;0.000027;0.0000;1.9;0;0.54;0.6448;0;0.0000;0.9771;23.3644;0.5470",
    "39;-10.61;-24;5.48;0;-4.01;0.0093;0.5629;0.000027;0.0000;1.9;0;0.54;0.5736;0;0.0000;0.9960;24.3415;0.5971",
    "40;-11.17;-24;5.32;0;-4.01;0.0093;0.5583;0.000027;0.0000;1.9;0;0.54;0.5603;0;0.0000;0.9979;25.3375;0.6442",
    "41;-11.73;-24;4.8;0;-4.01;0.0093;0.5933;0.000027;0.0000;1.9;0;0.54;0.5175;0;0.0000;0.9999;26.3354;0.6872",
    "42;-12.32;-24;5.83;0;-4.01;0.0093;0.4528;0.000027;0.0000;1.9;0;0.54;0.6033;0;0.0000;0.9898;27.3352;0.7258",
    "43;-12.78;-24;6.43;0;-4.01;0.0093;0.3726;0.000027;0.0000;1.9;0;0.54;0.6553;0;0.0000;0.9732;28.3251;0.7597",
    "44;-13.15;-24;6.55;0;-4.01;0.0093;0.3481;0.000027;0.0000;1.9;0;0.54;0.6659;0;0.0000;0.9690;29.2983;0.7892",
    "45;-13.50;-24;5.52;0;-4.01;0.0093;0.4376;0.000027;0.0000;1.9;0;0.54;0.5770;0;0.0000;0.9954;30.2673;0.8150",
    "46;-13.94;-24;4.1;0;-4.01;0.0093;0.5522;0.000027;0.0000;1.9;0;0.54;0.4618;0;0.0000;0.9918;31.2627;0.8382",
    "47;-14.49;-24;1.84;0;-4.01;0.0093;0.7219;0.000027;0.0000;1.9;0;0.54;0.2947;0;0.0000;0.8605;32.2545;0.8582",
    "48;-15.21;-24;4.85;0;-4.01;0.0093;0.4210;0.000027;0.0000;1.9;0;0.54;0.5216;0;0.0000;1.0000;33.1151;0.8735",
    "49;-15.63;-24;5.31;0;-4.01;0.0093;0.3650;0.000027;0.0000;1.9;0;0.54;0.5594;0;0.0000;0.9980;34.1150;0.8891",
    "50;-16.00;-24;6.06;0;-4.01;0.0093;0.2933;0.000027;0.0000;1.9;0;0.54;0.6230;0;0.0000;0.9844;35.1130;0.9025",
    "51;-16.29;-24;4.27;0;-4.01;0.0093;0.4109;0.000027;0.0000;1.9;0;0.54;0.4751;0;0.0000;0.9950;36.0974;0.9140",
    "52;-16.70;-24;2.56;0;-4.01;0.0093;0.5051;0.000027;0.0000;1.9;0;0.54;0.3459;0;0.0000;0.9227;37.0923;0.9241",
    "53;-17.21;-24;0.86;0;-4.01;0.0093;0.5776;0.000027;0.0000;1.9;0;0.54;0.2280;0;0.0000;0.7343;38.0151;0.9323",
    "54;-17.78;-24;0.57;0;-4.01;0.0093;0.5453;0.000027;0.0000;1.9;0;0.54;0.2088;0;0.0000;0.6851;38.7494;0.9381",
    "55;-18.33;-24;0.29;0;-4.01;0.0093;0.5122;0.000027;0.0000;1.9;0;0.54;0.1906;0;0.0000;0.6310;39.4344;0.9430",
    "56;-18.84;-24;0.29;0;-4.01;0.0093;0.4660;0.000027;0.0000;1.9;0;0.54;0.1906;0;0.0000;0.6310;40.0654;0.9471",
    "57;-19.31;-24;2.02;0;-4.01;0.0093;0.3484;0.000027;0.0000;1.9;0;0.54;0.3073;0;0.0000;0.8782;40.6964;0.9509",
    "58;-19.65;-24;0.4;0;-4.01;0.0093;0.3880;0.000027;0.0000;1.9;0;0.54;0.1978;0;0.0000;0.6531;41.5746;0.9556",
    "59;-20.04;-24;-0.16;0;-4.01;0.0093;0.3681;0.000027;0.0000;1.9;0;0.54;0.1619;0;0.0000;0.5271;42.2277;0.9588",
    "60;-20.41;-24;2.61;0;-4.01;0.0093;0.2467;0.000027;0.0000;1.9;0;0.54;0.3495;0;0.0000;0.9263;42.7547;0.9612",
    "61;-20.66;-24;4.72;0;-4.01;0.0093;0.1641;0.000027;0.0000;1.9;0;0.54;0.5111;0;0.0000;0.9996;43.6810;0.9650",
    "62;-20.82;-24;2.89;0;-4.01;0.0093;0.2102;0.000027;0.0000;1.9;0;0.54;0.3699;0;0.0000;0.9443;44.6806;0.9686",
    "63;-21.03;-24;0.01;0;-4.01;0.0093;0.2758;0.000027;0.0000;1.9;0;0.54;0.1727;0;0.0000;0.5691;45.6249;0.9717",
    "64;-21.31;-24;0.48;0;-4.01;0.0093;0.2384;0.000027;0.0000;1.9;0;0.54;0.2030;0;0.0000;0.6684;46.1940;0.9733",
    "65;-21.55;-24;2.65;0;-4.01;0.0093;0.1678;0.000027;0.0000;1.9;0;0.54;0.3524;0;0.0000;0.9290;46.8625;0.9751",
    "66;-21.71;-24;3.09;0;-4.01;0.0093;0.1469;0.000027;0.0000;1.9;0;0.54;0.3847;0;0.0000;0.9554;47.7915;0.9774",
    "67;-21.86;-24;4.02;0;-4.01;0.0093;0.1190;0.000027;0.0000;1.9;0;0.54;0.4555;0;0.0000;0.9900;48.7469;0.9795",
    "68;-21.98;-24;1.8;0;-4.01;0.0093;0.1541;0.000027;0.0000;1.9;0;0.54;0.2919;0;0.0000;0.8564;49.7369;0.9814",
    "69;-22.13;-24;3.83;0;-4.01;0.0093;0.1071;0.000027;0.0000;1.9;0;0.54;0.4408;0;0.0000;0.9851;50.5933;0.9829",
    "70;-22.24;-24;5.31;0;-4.01;0.0093;0.0767;0.000027;0.0000;1.9;0;0.54;0.5594;0;0.0000;0.9980;51.5784;0.9844",
    "71;-22.32;-24;1.89;0;-4.01;0.0093;0.1269;0.000027;0.0000;1.9;0;0.54;0.2982;0;0.0000;0.8656;52.5764;0.9858",
    "72;-22.44;-24;-0.14;0;-4.01;0.0093;0.1447;0.000027;0.0000;1.9;0;0.54;0.1632;0;0.0000;0.5322;53.4420;0.9869",
    "73;-22.59;-24;0.46;0;-4.01;0.0093;0.1252;0.000027;0.0000;1.9;0;0.54;0.2017;0;0.0000;0.6647;53.9742;0.9876",
    "74;-22.71;-24;1.11;0;-4.01;0.0093;0.1063;0.000027;0.0000;1.9;0;0.54;0.2447;0;0.0000;0.7719;54.6389;0.9883",
    "75;-22.82;-24;-0.16;0;-4.01;0.0093;0.1097;0.000027;0.0000;1.9;0;0.54;0.1619;0;0.0000;0.5271;55.4108;0.9891",
    "76;-22.93;-24;-1.55;0;-4.01;0.0093;0.0995;0.000027;0.0000;1.9;0;0.54;0.0773;0;0.0000;0.0000;55.9379;0.9896",
    "77;-23.03;-24;-2.36;0;-4.01;0.0093;0.0902;0.000027;0.0000;1.9;0;0.54;0.0307;0;0.0000;0.0000;55.9379;0.9896",
    "78;-23.12;-24;-2.25;0;-4.01;0.0093;0.0819;0.000027;0.0000;1.9;0;0.54;0.0369;0;0.0000;0.0000;55.9379;0.9896",
    "79;-23.20;-24;-1.27;0;-4.01;0.0093;0.0742;0.000027;0.0000;1.9;0;0.54;0.0939;0;0.0000;0.0506;55.9379;0.9896",
    "80;-23.28;-24;-3.96;0;-4.01;0.0093;0.0673;0.000027;0.0000;1.9;9.36E-14;0.54;0.0228;0;0.0000;0.0000;55.9885;0.9896",
    "81;-23.34;-24;-2.44;0;-4.01;0.0093;0.0611;0.000027;0.0000;1.9;0;0.54;0.0262;0;0.0000;0.0000;55.9885;0.9896",
    "82;-23.40;-24;-3.23;0;-4.01;0.0093;0.0554;0.000027;0.0000;1.9;1.91E-14;0.54;0.0228;0;0.0000;0.0000;55.9885;0.9896",
    "83;-23.46;-24;-1.37;0;-4.01;0.0093;0.0502;0.000027;0.0000;1.9;0;0.54;0.0879;0;0.0000;0.0000;55.9885;0.9896",
    "84;-23.51;-24;-2.28;0;-4.01;0.0093;0.0456;0.000027;0.0000;1.9;0;0.54;0.0352;0;0.0000;0.0000;55.9885;0.9896",
    "85;-23.56;-24;-3.54;0;-4.01;0.0093;0.0413;0.000027;0.0000;1.9;2.57E-14;0.54;0.0228;0;0.0000;0.0000;55.9885;0.9896",
    "86;-23.60;-24;-7.56;0;-4.01;0.0093;0.0375;0.000027;0.0000;1.9;3.95E-11;0.54;0.0228;0;0.0000;0.0000;55.9885;0.9896",
    "87;-23.63;-24;-8.27;0;-4.01;0.0093;0.0340;0.000027;0.0000;1.9;1.36E-10;0.54;0.0228;0;0.0000;0.0000;55.9885;0.9896",
    "88;-23.67;-24;-9.01;0;-4.01;0.0093;0.0308;0.000027;0.0000;1.9;4.95E-10;0.54;0.0228;0;0.0000;0.0000;55.9885;0.9896",
    "89;-23.70;-24;-3.33;0;-4.01;0.0093;0.0280;0.000027;0.0000;1.9;1.33E-14;0.54;0.0228;0;0.0000;0.0000;55.9885;0.9896",
    "90;-23.73;-24;-1.9;0;-4.01;0.0093;0.0254;0.000027;0.0000;1.9;0;0.54;0.0569;0;0.0000;0.0000;55.9885;0.9896",
    "91;-23.75;-24;-0.42;0;-4.01;0.0093;0.0230;0.000027;0.0000;1.9;0;0.54;0.1457;0;0.0000;0.4545;55.9885;0.9896",
    "92;-23.78;-24;-1.76;0;-4.01;0.0093;0.0000;0.000027;0.0060;1.9;0;0.54;0.0650;0;0.0000;0.0000;56.4430;0.9900",
    "93;-23.77;-24;-2.51;0;-4.01;0.0093;0.0000;0.000027;0.0018;1.9;0;0.54;0.0228;0;0.0000;0.0000;56.4430;0.9900",
    "94;-23.77;-24;-0.61;0;-4.01;0.0093;0.0000;0.000027;0.0208;1.9;0;0.54;0.1339;0;0.0000;0.3934;56.4430;0.9900",
    "95;-23.75;-24;-1.99;0;-4.01;0.0093;0.0000;0.000027;0.0043;1.9;0;0.54;0.0517;0;0.0000;0.0000;56.8364;0.9904",
    "96;-23.74;-24;-7.6;0;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;3.25E-11;0.54;0.0228;0;0.0000;0.0000;56.8364;0.9904",
    "97;-23.74;-24;-6.28;10;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;2.86E-12;0.54;0.0228;0.8;0.0098;0.0000;56.8364;0.9904",
    "98;-23.73;-24;-0.56;9;-4.01;0.0093;0.0000;0.000027;0.0217;1.9;0;0.54;0.1370;0.72;0.0533;0.4103;56.8364;0.9904",
    "99;-23.66;-24;-0.16;8;-4.01;0.0093;0.0000;0.000027;0.0300;1.9;0;0.54;0.1619;0.64;0.0560;0.5271;57.2467;0.9907",
    "100;-23.57;-24;-0.16;7;-4.01;0.0093;0.0000;0.000027;0.0299;1.9;0;0.54;0.1619;0.56;0.0490;0.5271;57.7738;0.9911",
    "101;-23.49;-24;-0.16;6;-4.01;0.0093;0.0000;0.000027;0.0298;1.9;0;0.54;0.1619;0.48;0.0420;0.5271;58.3008;0.9915",
    "102;-23.42;-24;-0.16;5;-4.01;0.0093;0.0000;0.000027;0.0297;1.9;0;0.54;0.1619;0.4;0.0350;0.5271;58.8279;0.9919",
    "103;-23.36;-24;-0.16;11;-4.01;0.0093;0.0000;0.000027;0.0296;1.9;0;0.54;0.1619;0.88;0.0770;0.5271;59.3550;0.9922",
    "104;-23.25;-24;-0.16;17;-4.01;0.0093;0.0000;0.000027;0.0294;1.9;0;0.54;0.1619;1;0.0875;0.5271;59.8821;0.9926",
    "105;-23.13;-24;-0.16;23;-4.01;0.0093;0.0000;0.000027;0.0292;1.9;0;0.54;0.1619;1;0.0875;0.5271;60.4091;0.9929",
    "106;-23.02;-24;-0.16;29;-4.01;0.0093;0.0000;0.000027;0.0291;1.9;0;0.54;0.1619;1;0.0875;0.5271;60.9362;0.9932",
    "107;-22.90;-24;-0.16;35;-4.01;0.0093;0.0000;0.000027;0.0289;1.9;0;0.54;0.1619;1;0.0875;0.5271;61.4633;0.9935",
    "108;-22.78;-24;-0.16;41;-4.01;0.0093;0.0000;0.000027;0.0287;1.9;0;0.54;0.1619;1;0.0875;0.5271;61.9904;0.9937",
    "109;-22.67;-24;-0.16;48;-4.01;0.0093;0.0000;0.000027;0.0285;1.9;0;0.54;0.1619;1;0.0875;0.5271;62.5174;0.9940",
    "110;-22.55;-24;-0.16;21;-4.01;0.0093;0.0000;0.000027;0.0283;1.9;0;0.54;0.1619;1;0.0875;0.5271;63.0445;0.9942",
    "111;-22.44;-24;-0.16;21;-4.01;0.0093;0.0000;0.000027;0.0282;1.9;0;0.54;0.1619;1;0.0875;0.5271;63.5716;0.9945",
    "112;-22.32;-24;-0.16;21;-4.01;0.0093;0.0000;0.000027;0.0280;1.9;0;0.54;0.1619;1;0.0875;0.5271;64.0987;0.9947",
    "113;-22.20;-24;-0.16;21;-4.01;0.0093;0.0000;0.000027;0.0278;1.9;0;0.54;0.1619;1;0.0875;0.5271;64.6257;0.9949",
    "114;-22.09;-24;-0.16;22;-4.01;0.0093;0.0000;0.000027;0.0276;1.9;0;0.54;0.1619;1;0.0875;0.5271;65.1528;0.9951",
    "115;-21.97;-24;-0.16;22;-4.01;0.0093;0.0000;0.000027;0.0275;1.9;0;0.54;0.1619;1;0.0875;0.5271;65.6799;0.9953",
    "116;-21.86;-24;-0.52;23;-4.01;0.0093;0.0000;0.000027;0.0203;1.9;0;0.54;0.1394;1;0.0753;0.4233;66.2070;0.9955",
    "117;-21.76;-24;-0.44;23;-4.01;0.0093;0.0000;0.000027;0.0216;1.9;0;0.54;0.1444;1;0.0780;0.4484;66.6303;0.9956",
    "118;-21.66;-24;-0.2;23;-4.01;0.0093;0.0000;0.000027;0.0262;1.9;0;0.54;0.1594;1;0.0861;0.5166;67.0787;0.9958",
    "119;-21.55;-24;-0.16;23;-4.01;0.0093;0.0000;0.000027;0.0268;1.9;0;0.54;0.1619;1;0.0875;0.5271;67.5953;0.9959",
    "120;-21.44;-24;-0.16;23;-4.01;0.0093;0.0000;0.000027;0.0266;1.9;0;0.54;0.1619;1;0.0875;0.5271;68.1224;0.9961",
    "121;-21.32;-24;-0.16;23;-4.01;0.0093;0.0000;0.000027;0.0265;1.9;0;0.54;0.1619;1;0.0875;0.5271;68.6495;0.9962",
    "122;-21.21;-24;-0.2;22;-4.01;0.0093;0.0000;0.000027;0.0255;1.9;0;0.54;0.1594;1;0.0861;0.5166;69.1765;0.9964",
    "123;-21.10;-24;-0.61;22;-4.01;0.0093;0.0000;0.000027;0.0180;1.9;0;0.54;0.1339;1;0.0723;0.3934;69.6931;0.9965",
    "124;-21.01;-24;-0.61;22;-4.01;0.0093;0.0000;0.000027;0.0179;1.9;0;0.54;0.1339;1;0.0723;0.3934;70.0866;0.9966",
    "125;-20.92;-24;-0.61;22;-4.01;0.0093;0.0000;0.000027;0.0178;1.9;0;0.54;0.1339;1;0.0723;0.3934;70.4800;0.9967",
    "126;-20.83;-24;-0.76;22;-4.01;0.0093;0.0000;0.000027;0.0154;1.9;0;0.54;0.1247;1;0.0673;0.3388;70.8734;0.9968",
    "127;-20.74;-24;-1.06;22;-4.01;0.0093;0.0000;0.000027;0.0115;1.9;0;0.54;0.1065;1;0.0575;0.2026;71.2123;0.9969",
    "128;-20.68;-24;-1.06;22;-4.01;0.0093;0.0000;0.000027;0.0114;1.9;0;0.54;0.1065;1;0.0575;0.2026;71.4149;0.9969",
    "129;-20.61;-24;-1.06;23;-4.01;0.0093;0.0000;0.000027;0.0114;1.9;0;0.54;0.1065;1;0.0575;0.2026;71.6175;0.9969",
    "130;-20.54;-24;-1.27;23;-4.01;0.0093;0.0000;0.000027;0.0091;1.9;0;0.54;0.0939;1;0.0507;0.0506;71.8201;0.9970",
    "131;-20.48;-24;-1.3;24;-4.01;0.0093;0.0000;0.000027;0.0088;1.9;0;0.54;0.0921;1;0.0497;0.0000;71.8708;0.9970",
    "132;-20.42;-24;-1.08;24;-4.01;0.0093;0.0000;0.000027;0.0110;1.9;0;0.54;0.1053;1;0.0568;0.1915;71.8708;0.9970",
    "133;-20.35;-24;-1.57;24;-4.01;0.0093;0.0000;0.000027;0.0063;1.9;0;0.54;0.0761;1;0.0411;0.0000;72.0623;0.9970",
    "134;-20.30;-24;-1.57;23;-4.01;0.0093;0.0000;0.000027;0.0063;1.9;0;0.54;0.0761;1;0.0411;0.0000;72.0623;0.9970",
    "135;-20.26;-24;-1.57;23;-4.01;0.0093;0.0000;0.000027;0.0063;1.9;0;0.54;0.0761;1;0.0411;0.0000;72.0623;0.9970",
    "136;-20.21;-24;-1.53;22;-4.01;0.0093;0.0000;0.000027;0.0066;1.9;0;0.54;0.0785;1;0.0424;0.0000;72.0623;0.9970",
    "137;-20.16;-24;-1.1;22;-4.01;0.0093;0.0000;0.000027;0.0106;1.9;0;0.54;0.1041;1;0.0562;0.1800;72.0623;0.9970",
    "138;-20.09;-24;-1.84;22;-4.01;0.0093;0.0000;0.000027;0.0044;1.9;0;0.54;0.0604;1;0.0326;0.0000;72.2422;0.9971",
    "139;-20.06;-24;-2.26;22;-4.01;0.0093;0.0000;0.000027;0.0023;1.9;0;0.54;0.0363;1;0.0196;0.0000;72.2422;0.9971",
    "140;-20.03;-24;-2.96;22;-4.01;0.0093;0.0000;0.000027;0.0005;1.9;0;0.54;0.0228;1;0.0123;0.0000;72.2422;0.9971",
    "141;-20.02;-24;-3;22;-4.01;0.0093;0.0000;0.000027;0.0004;1.9;0;0.54;0.0228;1;0.0123;0.0000;72.2422;0.9971",
    "142;-20.01;-24;-3.73;22;-4.01;0.0093;0.0000;0.000027;0.0000;1.9;2.53E-11;0.54;0.0228;1;0.0123;0.0000;72.2422;0.9971",
    "143;-20.00;-24;-2.57;22;-4.01;0.0093;0.0000;0.000027;0.0013;1.9;0;0.54;0.0228;1;0.0123;0.0000;72.2422;0.9971",
    "144;-19.98;-24;-2.21;22;-4.01;0.0093;0.0000;0.000027;0.0025;1.9;0;0.54;0.0392;1;0.0211;0.0000;72.2422;0.9971",
    "145;-19.96;-24;-2.44;22;-4.01;0.0093;0.0000;0.000027;0.0016;1.9;0;0.54;0.0262;1;0.0141;0.0000;72.2422;0.9971",
    "146;-19.94;-24;-3.02;22;-4.01;0.0093;0.0000;0.000027;0.0004;1.9;7.72E-12;0.54;0.0228;1;0.0123;0.0000;72.2422;0.9971",
    "147;-19.93;-24;-3.18;22;-4.01;0.0093;0.0000;0.000027;0.0002;1.9;1.06E-11;0.54;0.0228;1;0.0123;0.0000;72.2422;0.9971",
    "148;-19.92;-24;-2.22;22;-4.01;0.0093;0.0000;0.000027;0.0024;1.9;0;0.54;0.0386;1;0.0208;0.0000;72.2422;0.9971",
    "149;-19.90;-24;-1.76;22;-4.01;0.0093;0.0000;0.000027;0.0048;1.9;0;0.54;0.0650;1;0.0351;0.0000;72.2422;0.9971",
    "150;-19.86;-24;-1.51;22;-4.01;0.0093;0.0000;0.000027;0.0066;1.9;0;0.54;0.0797;1;0.0430;0.0000;72.2422;0.9971",
    "151;-19.81;-24;-1.95;22;-4.01;0.0093;0.0000;0.000027;0.0037;1.9;0;0.54;0.0540;1;0.0292;0.0000;72.2422;0.9971",
    "152;-19.77;-24;-1.97;22;-4.01;0.0093;0.0000;0.000027;0.0036;1.9;0;0.54;0.0529;1;0.0286;0.0000;72.2422;0.9971",
    "153;-19.74;-24;-2.57;22;-4.01;0.0093;0.0000;0.000027;0.0012;1.9;0;0.54;0.0228;1;0.0123;0.0000;72.2422;0.9971",
    "154;-19.73;-24;-3.19;22;-4.01;0.0093;0.0000;0.000027;0.0002;1.9;1.57E-11;0.54;0.0228;1;0.0123;0.0000;72.2422;0.9971",
    "155;-19.71;-24;-2.9;22;-4.01;0.0093;0.0000;0.000027;0.0006;1.9;0;0.54;0.0228;1;0.0123;0.0000;72.2422;0.9971",
    "156;-19.70;-24;-2.9;22;-4.01;0.0093;0.0000;0.000027;0.0006;1.9;0;0.54;0.0228;1;0.0123;0.0000;72.2422;0.9971",
    "157;-19.69;-24;-2.5;22;-4.01;0.0093;0.0000;0.000027;0.0014;1.9;0;0.54;0.0228;1;0.0123;0.0000;72.2422;0.9971",
    "158;-19.68;-24;-2.3;21;-4.01;0.0093;0.0000;0.000027;0.0021;1.9;0;0.54;0.0341;1;0.0184;0.0000;72.2422;0.9971",
    "159;-19.65;-24;-1.51;21;-4.01;0.0093;0.0000;0.000027;0.0065;1.9;0;0.54;0.0797;1;0.0430;0.0000;72.2422;0.9971",
    "160;-19.61;-24;-0.57;21;-4.01;0.0093;0.0000;0.000027;0.0170;1.9;0;0.54;0.1364;1;0.0736;0.4070;72.2422;0.9971",
    "161;-19.51;-24;-0.16;23;-4.01;0.0093;0.0000;0.000027;0.0237;1.9;0;0.54;0.1619;1;0.0875;0.5271;72.6492;0.9972",
    "162;-19.40;-24;-0.16;26;-4.01;0.0093;0.0000;0.000027;0.0235;1.9;0;0.54;0.1619;1;0.0875;0.5271;73.1763;0.9973",
    "163;-19.29;-24;-0.5;29;-4.01;0.0093;0.0000;0.000027;0.0177;1.9;0;0.54;0.1407;1;0.0760;0.4297;73.7033;0.9974",
    "164;-19.20;-24;-0.61;37;-4.01;0.0093;0.0000;0.000027;0.0160;1.9;0;0.54;0.1339;1;0.0723;0.3934;74.1331;0.9974",
    "165;-19.11;-24;-0.61;45;-4.01;0.0093;0.0000;0.000027;0.0159;1.9;0;0.54;0.1339;1;0.0723;0.3934;74.5265;0.9975",
    "166;-19.02;-24;-0.61;54;-4.01;0.0093;0.0000;0.000027;0.0158;1.9;0;0.54;0.1339;1;0.0723;0.3934;74.9199;0.9976",
    "167;-18.93;-24;-0.61;29;-4.01;0.0093;0.0000;0.000027;0.0157;1.9;0;0.54;0.1339;1;0.0723;0.3934;75.3133;0.9976",
    "168;-18.85;-24;-0.46;29;-4.01;0.0093;0.0000;0.000027;0.0178;1.9;0;0.54;0.1432;1;0.0773;0.4423;75.7068;0.9977",
    "169;-18.75;-24;-0.16;29;-4.01;0.0093;0.0000;0.000027;0.0225;1.9;0;0.54;0.1619;1;0.0875;0.5271;76.1490;0.9978",
    "170;-18.64;-24;-0.16;29;-4.01;0.0093;0.0000;0.000027;0.0224;1.9;0;0.54;0.1619;1;0.0875;0.5271;76.6761;0.9978",
    "171;-18.53;-24;-0.16;29;-4.01;0.0093;0.0000;0.000027;0.0222;1.9;0;0.54;0.1619;1;0.0875;0.5271;77.2032;0.9979",
    "172;-18.42;-24;-0.16;29;-4.01;0.0093;0.0000;0.000027;0.0220;1.9;0;0.54;0.1619;1;0.0875;0.5271;77.7303;0.9980",
    "173;-18.31;-24;-0.16;29;-4.01;0.0093;0.0000;0.000027;0.0219;1.9;0;0.54;0.1619;1;0.0875;0.5271;78.2573;0.9980",
    "174;-18.20;-24;-0.16;29;-4.01;0.0093;0.0000;0.000027;0.0217;1.9;0;0.54;0.1619;1;0.0875;0.5271;78.7844;0.9981",
    "175;-18.09;-24;-0.16;28;-4.01;0.0093;0.0000;0.000027;0.0215;1.9;0;0.54;0.1619;1;0.0875;0.5271;79.3115;0.9982",
    "176;-17.98;-24;-0.16;28;-4.01;0.0093;0.0000;0.000027;0.0214;1.9;0;0.54;0.1619;1;0.0875;0.5271;79.8386;0.9982",
    "177;-17.88;-24;-0.16;27;-4.01;0.0093;0.0000;0.000027;0.0212;1.9;0;0.54;0.1619;1;0.0875;0.5271;80.3656;0.9983",
    "178;-17.77;-24;-0.16;27;-4.01;0.0093;0.0000;0.000027;0.0210;1.9;0;0.54;0.1619;1;0.0875;0.5271;80.8927;0.9983",
    "179;-17.66;-24;-0.16;26;-4.01;0.0093;0.0000;0.000027;0.0209;1.9;0;0.54;0.1619;1;0.0875;0.5271;81.4198;0.9984",
    "180;-17.55;-24;-0.16;26;-4.01;0.0093;0.0000;0.000027;0.0207;1.9;0;0.54;0.1619;1;0.0875;0.5271;81.9469;0.9984",
    "181;-17.44;-24;-0.16;26;-4.01;0.0093;0.0000;0.000027;0.0205;1.9;0;0.54;0.1619;1;0.0875;0.5271;82.4739;0.9985",
    "182;-17.33;-24;-0.16;26;-4.01;0.0093;0.0000;0.000027;0.0204;1.9;0;0.54;0.1619;1;0.0875;0.5271;83.0010;0.9985",
    "183;-17.23;-24;-0.16;25;-4.01;0.0093;0.0000;0.000027;0.0202;1.9;0;0.54;0.1619;1;0.0875;0.5271;83.5281;0.9986",
    "184;-17.12;-24;-0.16;25;-4.01;0.0093;0.0000;0.000027;0.0200;1.9;0;0.54;0.1619;1;0.0875;0.5271;84.0552;0.9986",
    "185;-17.01;-24;-0.48;24;-4.01;0.0093;0.0000;0.000027;0.0153;1.9;0;0.54;0.1419;1;0.0766;0.4360;84.5822;0.9987",
    "186;-16.92;-24;-0.2;24;-4.01;0.0093;0.0000;0.000027;0.0191;1.9;0;0.54;0.1594;1;0.0861;0.5166;85.0183;0.9987",
    "187;-16.81;-24;-0.16;24;-4.01;0.0093;0.0000;0.000027;0.0196;1.9;0;0.54;0.1619;1;0.0875;0.5271;85.5349;0.9987",
    "188;-16.71;-24;-0.16;24;-4.01;0.0093;0.0000;0.000027;0.0194;1.9;0;0.54;0.1619;1;0.0875;0.5271;86.0620;0.9988",
    "189;-16.60;-24;-0.16;24;-4.01;0.0093;0.0000;0.000027;0.0193;1.9;0;0.54;0.1619;1;0.0875;0.5271;86.5890;0.9988",
    "190;-16.49;-24;-0.22;24;-4.01;0.0093;0.0000;0.000027;0.0182;1.9;0;0.54;0.1582;1;0.0854;0.5113;87.1161;0.9989",
    "191;-16.39;-24;-0.61;24;-4.01;0.0093;0.0000;0.000027;0.0130;1.9;0;0.54;0.1339;1;0.0723;0.3934;87.6274;0.9989",
    "192;-16.30;-24;-0.61;24;-4.01;0.0093;0.0000;0.000027;0.0129;1.9;0;0.54;0.1339;1;0.0723;0.3934;88.0208;0.9989",
    "193;-16.22;-24;-0.61;24;-4.01;0.0093;0.0000;0.000027;0.0128;1.9;0;0.54;0.1339;1;0.0723;0.3934;88.4142;0.9989",
    "194;-16.13;-24;-0.61;24;-4.01;0.0093;0.0000;0.000027;0.0128;1.9;0;0.54;0.1339;1;0.0723;0.3934;88.8077;0.9990",
    "195;-16.05;-24;-0.61;24;-4.01;0.0093;0.0000;0.000027;0.0127;1.9;0;0.54;0.1339;1;0.0723;0.3934;89.2011;0.9990",
    "196;-15.96;-24;-0.61;24;-4.01;0.0093;0.0000;0.000027;0.0126;1.9;0;0.54;0.1339;1;0.0723;0.3934;89.5945;0.9990",
    "197;-15.88;-24;-0.61;23;-4.01;0.0093;0.0000;0.000027;0.0125;1.9;0;0.54;0.1339;1;0.0723;0.3934;89.9880;0.9990",
    "198;-15.79;-24;-0.61;23;-4.01;0.0093;0.0000;0.000027;0.0124;1.9;0;0.54;0.1339;1;0.0723;0.3934;90.3814;0.9990",
    "199;-15.71;-24;-0.61;22;-4.01;0.0093;0.0000;0.000027;0.0123;1.9;0;0.54;0.1339;1;0.0723;0.3934;90.7748;0.9991",
    "200;-15.63;-24;-0.55;22;-4.01;0.0093;0.0000;0.000027;0.0129;1.9;0;0.54;0.1376;1;0.0743;0.4136;91.1682;0.9991",
    "201;-15.54;-24;-0.16;22;-4.01;0.0093;0.0000;0.000027;0.0176;1.9;0;0.54;0.1619;1;0.0875;0.5271;91.5818;0.9991",
    "202;-15.43;-24;-0.16;20;-4.01;0.0093;0.0000;0.000027;0.0175;1.9;0;0.54;0.1619;1;0.0875;0.5271;92.1089;0.9991",
    "203;-15.33;-24;-0.16;19;-4.01;0.0093;0.0000;0.000027;0.0173;1.9;0;0.54;0.1619;1;0.0875;0.5271;92.6360;0.9992",
    "204;-15.22;-24;-0.16;18;-4.01;0.0093;0.0000;0.000027;0.0171;1.9;0;0.54;0.1619;1;0.0875;0.5271;93.1630;0.9992",
    "205;-15.12;-24;-0.16;16;-4.01;0.0093;0.0000;0.000027;0.0170;1.9;0;0.54;0.1619;1;0.0875;0.5271;93.6901;0.9992",
    "206;-15.01;-24;-0.16;14;-4.01;0.0093;0.0000;0.000027;0.0168;1.9;0;0.54;0.1619;1;0.0875;0.5271;94.2172;0.9992",
    "207;-14.91;-24;-0.16;12;-4.01;0.0093;0.0000;0.000027;0.0167;1.9;0;0.54;0.1619;0.96;0.0840;0.5271;94.7443;0.9992",
    "208;-14.81;-24;-0.16;10;-4.01;0.0093;0.0000;0.000027;0.0165;1.9;0;0.54;0.1619;0.8;0.0700;0.5271;95.2713;0.9993",
    "209;-14.72;-24;-0.16;10;-4.01;0.0093;0.0000;0.000027;0.0164;1.9;0;0.54;0.1619;0.8;0.0700;0.5271;95.7984;0.9993",
    "210;-14.64;-24;-0.16;9;-4.01;0.0093;0.0000;0.000027;0.0162;1.9;0;0.54;0.1619;0.72;0.0630;0.5271;96.3255;0.9993",
    "211;-14.56;-24;-0.39;8;-4.01;0.0093;0.0000;0.000027;0.0134;1.9;0;0.54;0.1475;0.64;0.0510;0.4634;96.8526;0.9993",
    "212;-14.49;-24;-0.16;7;-4.01;0.0093;0.0000;0.000027;0.0160;1.9;0;0.54;0.1619;0.56;0.0490;0.5271;97.3160;0.9993",
    "213;-14.43;-24;-0.16;6;-4.01;0.0093;0.0000;0.000027;0.0159;1.9;0;0.54;0.1619;0.48;0.0420;0.5271;97.8431;0.9994",
    "214;-14.37;-24;-0.16;5;-4.01;0.0093;0.0000;0.000027;0.0158;1.9;0;0.54;0.1619;0.4;0.0350;0.5271;98.3702;0.9994",
    "215;-14.32;-24;-0.16;5;-4.01;0.0093;0.0000;0.000027;0.0158;1.9;0;0.54;0.1619;0.4;0.0350;0.5271;98.8972;0.9994",
    "216;-14.27;-24;-0.16;5;-4.01;0.0093;0.0000;0.000027;0.0157;1.9;0;0.54;0.1619;0.4;0.0350;0.5271;99.4243;0.9994",
    "217;-14.22;-24;-0.16;5;-4.01;0.0093;0.0000;0.000027;0.0156;1.9;0;0.54;0.1619;0.4;0.0350;0.5271;99.9514;0.9994",
    "218;-14.17;-24;-0.16;5;-4.01;0.0093;0.0000;0.000027;0.0155;1.9;0;0.54;0.1619;0.4;0.0350;0.5271;100.4785;0.9994",
    "219;-14.12;-24;-0.16;5;-4.01;0.0093;0.0000;0.000027;0.0155;1.9;0;0.54;0.1619;0.4;0.0350;0.5271;101.0055;0.9995",
    "220;-14.07;-24;-0.16;5;-4.01;0.0093;0.0000;0.000027;0.0154;1.9;0;0.54;0.1619;0.4;0.0350;0.5271;101.5326;0.9995",
    "221;-14.02;-24;-0.16;5;-4.01;0.0093;0.0000;0.000027;0.0153;1.9;0;0.54;0.1619;0.4;0.0350;0.5271;102.0597;0.9995",
    "222;-13.97;-24;-0.16;5;-4.01;0.0093;0.0000;0.000027;0.0152;1.9;0;0.54;0.1619;0.4;0.0350;0.5271;102.5868;0.9995",
    "223;-13.92;-24;-0.16;5;-4.01;0.0093;0.0000;0.000027;0.0151;1.9;0;0.54;0.1619;0.4;0.0350;0.5271;103.1138;0.9995",
    "224;-13.87;-24;-0.18;5;-4.01;0.0093;0.0000;0.000027;0.0148;1.9;0;0.54;0.1607;0.4;0.0347;0.5219;103.6409;0.9995",
    "225;-13.82;-24;-0.14;4;-4.01;0.0093;0.0000;0.000027;0.0152;1.9;0;0.54;0.1632;0.32;0.0282;0.5322;104.1628;0.9995",
    "226;-13.77;-24;-0.16;3;-4.01;0.0093;0.0000;0.000027;0.0149;1.9;0;0.54;0.1619;0.24;0.0210;0.5271;104.6950;0.9995",
    "227;-13.74;-24;-0.16;2;-4.01;0.0093;0.0000;0.000027;0.0149;1.9;0;0.54;0.1619;0.16;0.0140;0.5271;105.2221;0.9996",
    "228;-13.71;-24;-0.16;1;-4.01;0.0093;0.0000;0.000027;0.0148;1.9;0;0.54;0.1619;0.08;0.0070;0.5271;105.7492;0.9996",
    "229;-13.69;-24;-0.16;0;-4.01;0.0093;0.0000;0.000027;0.0148;1.9;0;0.54;0.1619;0;0.0000;0.5271;106.2762;0.9996",
    "230;-13.67;-24;0.3;0;-4.01;0.0093;0.0000;0.000027;0.0207;1.9;0;0.54;0.1913;0;0.0000;0.6330;106.8033;0.9996",
    "231;-13.65;-24;2.69;0;-4.01;0.0093;0.0000;0.000027;0.0780;1.9;0;0.54;0.3553;0;0.0000;0.9317;107.4363;0.9996",
    "232;-13.57;-24;2.01;0;-4.01;0.0093;0.0000;0.000027;0.0561;1.9;0;0.54;0.3066;0;0.0000;0.8773;108.3681;0.9996",
    "233;-13.52;-24;3.39;0;-4.01;0.0093;0.0000;0.000027;0.1036;1.9;0;0.54;0.4072;0;0.0000;0.9695;109.2453;0.9996",
    "234;-13.41;-24;5.74;0;-4.01;0.0093;0.0000;0.000027;0.2346;1.9;0;0.54;0.5956;0;0.0000;0.9917;110.2149;0.9996",
    "235;-13.18;-24;6.46;0;-4.01;0.0093;0.0000;0.000027;0.2834;1.9;0;0.54;0.6579;0;0.0000;0.9722;111.2065;0.9997",
    "236;-12.89;-24;5.49;0;-4.01;0.0093;0.0000;0.000027;0.2051;1.9;0;0.54;0.5745;0;0.0000;0.9958;112.1787;0.9997",
    "237;-12.69;-24;5.88;0;-4.01;0.0093;0.0000;0.000027;0.2261;1.9;0;0.54;0.6075;0;0.0000;0.9887;113.1746;0.9997",
    "238;-12.46;-24;5.29;0;-4.01;0.0093;0.0000;0.000027;0.1830;1.9;0;0.54;0.5578;0;0.0000;0.9982;114.1633;0.9997",
    "239;-12.28;-24;4.91;0;-4.01;0.0093;0.0000;0.000027;0.1580;1.9;0;0.54;0.5265;0;0.0000;1.0000;115.1615;0.9997",
    "240;-12.12;-24;5.31;0;-4.01;0.0093;0.0000;0.000027;0.1768;1.9;0;0.54;0.5594;0;0.0000;0.9980;116.1615;0.9997",
    "241;-11.95;-24;5.89;0;-4.01;0.0093;0.0000;0.000027;0.2073;1.9;0;0.54;0.6084;0;0.0000;0.9885;117.1595;0.9997",
    "242;-11.74;-24;7.24;0;-4.01;0.0093;0.0000;0.000027;0.2964;1.9;0;0.54;0.7281;0;0.0000;0.9394;118.1480;0.9997",
    "243;-11.44;-24;8.05;0;-4.01;0.0093;0.0000;0.000027;0.3512;1.9;0;0.54;0.8040;0;0.0000;0.8936;119.0874;0.9998",
    "244;-11.09;-24;7.93;0;-4.01;0.0093;0.0000;0.000027;0.3247;1.9;0;0.54;0.7925;0;0.0000;0.9011;119.9810;0.9998",
    "245;-10.77;-24;9.01;0;-4.01;0.0093;0.0000;0.000027;0.4018;1.9;0;0.54;0.8980;0;0.0000;0.8250;120.8821;0.9998",
    "246;-10.36;-24;8.49;0;-4.01;0.0093;0.0000;0.000027;0.3344;1.9;0;0.54;0.8465;0;0.0000;0.8640;121.7071;0.9998",
    "247;-10.03;-24;8.39;0;-4.01;0.0093;0.0000;0.000027;0.3093;1.9;0;0.54;0.8367;0;0.0000;0.8710;122.5711;0.9998",
    "248;-9.72;-24;9.08;0;-4.01;0.0093;0.0000;0.000027;0.3452;1.9;0;0.54;0.9050;0;0.0000;0.8194;123.4421;0.9998",
    "249;-9.38;-24;8.88;0;-4.01;0.0093;0.0000;0.000027;0.3097;1.9;0;0.54;0.8850;0;0.0000;0.8351;124.2615;0.9998",
    "250;-9.07;-24;10;0;-4.01;0.0093;0.0000;0.000027;0.3747;1.9;0;0.54;0.9999;0;0.0000;0.7393;125.0967;0.9998",
    "251;-8.69;-24;10;0;-4.01;0.0093;0.0000;0.000027;0.3470;1.9;0;0.54;0.9999;0;0.0000;0.7393;125.8360;0.9998"]

class Container(object):
    pass

header_names = headers.split(";")[1:]
frostol_testdata = {}
for strline in raw_data:
    vline = strline.split(";")
    day_no = int(vline.pop(0))
    c = Container()
    for hname, value in zip(header_names, vline):
        setattr(c, hname, float(value))
    frostol_testdata[day_no] = c
