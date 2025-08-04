from flask import Flask, render_template, request
import math

app = Flask(__name__)

@app.route('/')
def base():
    return render_template('base.html')



#Capacity_4G_Calculations
@app.route("/4G_form_A", methods=["GET", "POST"])
def cap_4G():
    if request.method == "POST":

        try:
            #for FDD
            No_cells_site = int(request.form["No_cells_site"])
            Q = float(request.form["Q"]) / 100
            type_CP = request.form["type_CP"].title()
            No_antennas = int(request.form["No_antennas"])
            type_mod = request.form["type_mod"].upper()
            CCH = float(request.form["CCH"]) / 100

            #for calculation of busy hour active users

            Population = int(request.form["Population"])
            mobile_pent = float(request.form["mobile_pent"]) / 100
            market_sh = float(request.form["market_sh"]) / 100
            BHAU = float(request.form["BHAU"]) / 100

            BLER = float(request.form["BLER"]) / 100

            #for TDD
            DL_ratio = float(request.form["DL_ratio"])

            #for total traffic
            #=>voice calls
            voice_call = float(request.form["voice_call"]) / 100
            session_bearer_VC = float(request.form["session_bearer_VC"]) / 1000
            session_time_VC = float(request.form["session_time_VC"])
            duty_ratio_VC = float(request.form["duty_ratio_VC"]) / 100

            #=>browsing
            browsing = float(request.form["browsing"]) / 100
            session_bearer_brow = float(request.form["session_bearer_brow"]) / 1000
            session_time_brow = float(request.form["session_time_brow"])
            duty_ratio_brow = float(request.form["duty_ratio_brow"]) / 100

            #=>gaming
            gaming = float(request.form["gaming"]) / 100
            session_bearer_gam = float(request.form["session_bearer_gam"]) / 1000
            session_time_gam = float(request.form["session_time_gam"])
            duty_ratio_gam = float(request.form["duty_ratio_gam"]) / 100

            #=>streaming
            streaming = float(request.form["streaming"]) / 100
            session_bearer_strem = float(request.form["session_bearer_strem"]) / 1000
            session_time_strem = float(request.form["session_time_strem"])
            duty_ratio_strem = float(request.form["duty_ratio_strem"]) / 100

            # Calculations for modulation order & coding rate
            mod_types = {
                "QPSK": (2, .33),
                "16QAM": (4, .75),
                "64QAM": (6, .93)
            }

            Mod_order, coding_rate = mod_types[type_mod]

            #for cycle prefix

            if type_CP == "Short":
                NRE = (12 * 7) - (4 * No_antennas)
            elif type_CP == "Long":
                NRE = (12 * 6) - (4 * No_antennas)

            NRB = 50

            No_active_users = Population * mobile_pent * market_sh * BHAU  # active users

            #session traffic voice
            def session_traffic_voice(No_active_users, session_bearer_VC, session_time_VC, duty_ratio_VC, BLER, voice_call):
                session_traffic = session_bearer_VC * session_time_VC * duty_ratio_VC / (1 - BLER)
                total_traffic_VC = voice_call * No_active_users * session_traffic
                return total_traffic_VC

            #session traffic browsing
            def session_traffic_browsing(No_active_users, session_bearer_brow, session_time_brow, duty_ratio_brow, BLER, browsing):
                session_traffic = session_bearer_brow * session_time_brow * duty_ratio_brow / (1 - BLER)
                total_traffic_brow = browsing * No_active_users * session_traffic
                return total_traffic_brow

            #session traffic gaming
            def session_traffic_gaming(No_active_users, session_bearer_gam, session_time_gam, duty_ratio_gam, BLER, gaming):
                session_traffic = session_bearer_gam * session_time_gam * duty_ratio_gam / (1 - BLER)
                total_traffic_gam = gaming * No_active_users * session_traffic
                return total_traffic_gam

            #session traffic streaming
            def session_traffic_streaming(No_active_users, session_bearer_strem, session_time_strem, duty_ratio_strem, BLER, streaming):
                session_traffic = session_bearer_strem * session_time_strem * duty_ratio_strem / (1 - BLER)
                total_traffic_strem = streaming * No_active_users * session_traffic
                return total_traffic_strem

            A = session_traffic_voice(No_active_users, session_bearer_VC, session_time_VC, duty_ratio_VC, BLER, voice_call)

            B = session_traffic_browsing(No_active_users, session_bearer_brow, session_time_brow, duty_ratio_brow, BLER, browsing)

            C = session_traffic_gaming(No_active_users, session_bearer_gam, session_time_gam, duty_ratio_gam, BLER, gaming)

            D = session_traffic_streaming(No_active_users, session_bearer_strem, session_time_strem, duty_ratio_strem, BLER, streaming)

            total_traffic_area = (A + B + C + D) / 3600

            #FDD

            def FDD_calc(NRB, NRE, Mod_order, coding_rate, CCH, No_cells_site):
                T_cell = 2000 * NRB * NRE * Mod_order * coding_rate * (1 - CCH) * 10**-6  # to be in MHz
                T_site = T_cell * No_cells_site * Q  # in MHz
                return T_site

            site_traffic_fdd = FDD_calc(NRB, NRE, Mod_order, coding_rate, CCH, No_cells_site)

            N_fdd = math.ceil(total_traffic_area / site_traffic_fdd)

            #TDD

            def TDD_calc(NRB, NRE, Mod_order, coding_rate, CCH, No_cells_site):
                T_cell = 2000 * NRB * NRE * Mod_order * coding_rate * (1 - CCH) * 10**-6  # to be in MHz
                T_site = T_cell * No_cells_site * Q * DL_ratio  # in MHz
                return T_site

            site_traffic_tdd = TDD_calc(NRB, NRE, Mod_order, coding_rate, CCH, No_cells_site)

            N_tdd = math.ceil(total_traffic_area / site_traffic_tdd)

            return render_template("4G_form_A.html", total_traffic_area = total_traffic_area, site_traffic = site_traffic_fdd, N_fdd = N_fdd, site_traffic_tdd = site_traffic_tdd, N_tdd = N_tdd)
        
        except Exception as e:
            return f"Error Occurred: {e}"


    return render_template("4G_form_A.html") # for GET



#Coverage_4G_Calculations
@app.route("/4G_form_B", methods=["GET", "POST"])
def cov_4G():
    if request.method == "POST":
        
        try:
            total_area = float(request.form["total_area"])

            #DATA FOR DL

            Txpwr_DL = float(request.form["Txpwr_DL"])
            IM_DL = float(request.form["IM_DL"])
            SINR_DL = float(request.form["SINR_DL"])
            PRB_DL = int(request.form["PRB_DL"])

            #DATA FOR UL
            Txpwr_UL = float(request.form["Txpwr_UL"])
            IM_UL = float(request.form["IM_UL"])
            SINR_UL = float(request.form["SINR_UL"])
            PRB_UL = int(request.form["PRB_UL"])

            
            #Common Data
            frequency = int(request.form["frequency"])
            carrier = int(request.form["carrier"])
            feeder_loss = float(request.form["feeder_loss"])
            coverage_prob = int(request.form["coverage_prob"])
            clutter_type = (request.form["clutter_type"]).title()

            #Constant Data
            body_loss = 0 
            UE_NF = 7   #dB
            H_bs = 30   #m
            H_UE = 1.5  #m

            #UE antenna gain
            Rxant_gain_DL = Txant_gain_UL = 6
            Kb = 1.38 * 10**-23
            T = 290

            #calculations of eNB antenna gain according to Frequency

            
            if frequency == 1500 or frequency > 1500:
                Rxant_gain_UL = Txant_gain_DL = 18

            elif frequency == 900 or frequency < 900:
                Rxant_gain_UL = Txant_gain_DL = 15


            # COVERAGE PROBABILITY MARGINS

            slow_fading_margins = {
                98: {"Rural": 5.5, "Sub-Urban": 5.5, "Urban": 5.9, "Dense-Urban": 6.1},
                95: {"Rural": 2.9, "Sub-Urban": 2.9, "Urban": 3.9, "Dense-Urban": 4.1},
                90: {"Rural": 0.5, "Sub-Urban": 0.5, "Urban": 1.8, "Dense-Urban": 3.1},
                85: {"Rural": -1.2, "Sub-Urban": -1.2, "Urban": 0.2, "Dense-Urban": 0.6}
            }
            slow_fading_margin = slow_fading_margins[coverage_prob][clutter_type]


            # CLUTTER TYPE LOSS VALUES

            clutter_losses = {
                "Rural": (10, 0),
                "Sub-urban": (15, 1),
                "Urban": (20, 2),
                "Dense-Urban": (25, 2)
            }
            penetration_loss, fast_fading_margin = clutter_losses[clutter_type]

            #calculations of Noise Figure of eNB

            eNB_NF_values = [2, 2.3, 2.5]
            eNB_freq_values = [2100, 1800, 2600]

            if frequency == eNB_freq_values[0]:
                eNB_NF = eNB_NF_values[0]

            elif frequency == eNB_freq_values[1]:
                eNB_NF = eNB_NF_values[1]

            else:
                eNB_NF = eNB_NF_values[2]


            #CALCULATIONS

            losses_margins = penetration_loss + body_loss + fast_fading_margin + slow_fading_margin + IM_UL
            #1- senstivity

            ###For Dl => UE senstivity
            Rxsens_DL = 10 * math.log10(T * Kb * PRB_DL * 180000 * 1000) + UE_NF + SINR_DL

            ###For UL => eNB senstivity
            Rxsens_UL = 10 * math.log10(T * Kb * PRB_UL * 180000 * 1000) + eNB_NF + SINR_UL

            if frequency > 1500 :

                # 2- MAPL Calculation for DL
        
                def DL_Calculations(H_UE, H_bs, total_area):

                    MAPL_DL = Txpwr_DL - feeder_loss + Txant_gain_DL - losses_margins + Rxant_gain_DL - Rxsens_DL 
                    l = MAPL_DL
                    
                    a = (1.1 * math.log10(frequency) - 0.7) * H_UE - (1.56 * math.log10(frequency) - 0.8)
                    log_R = (l - 46.3 - 33.9 *math.log10(frequency) + 13.82 * math.log10(H_bs) + a) / (44.9 - 6.55 * math.log10(H_bs))
                    
                    R_DL = 10 ** log_R  # Site radius in kilometers
                    A_site_DL = 1.94 * R_DL ** 2  # Area covered per site in km²
                    N_DL = math.ceil(total_area / A_site_DL)  # Number of sites required

                    return MAPL_DL, R_DL, A_site_DL, N_DL

                # 3- MAPL Calculation for UL
                def UL_Calculations(H_UE, H_bs, total_area):

                    MAPL_UL = Txpwr_UL - feeder_loss + Txant_gain_UL - losses_margins + Rxant_gain_UL - Rxsens_UL 
                    l = MAPL_UL
                    
                    a = (1.1 * math.log10(frequency) - 0.7) * H_UE - (1.56 * math.log10(frequency) - 0.8)
                    log_R = (l - 46.3 - 33.9 *math.log10(frequency) + 13.82 * math.log10(H_bs) + a) / (44.9 - 6.55 * math.log10(H_bs))
                    
                    R_UL = 10 ** log_R  # Site radius in kilometers
                    A_site_UL = 1.94 * R_UL ** 2  # Area covered per site in km²
                    N_UL = math.ceil(total_area / A_site_UL)  # Number of sites required

                    return MAPL_UL, R_UL, A_site_UL, N_UL



            if frequency < 1500 :

                # 2- MAPL Calculation for DL
        
                def DL_Calculations(H_UE, H_bs, total_area):

                    MAPL_DL = Txpwr_DL - feeder_loss + Txant_gain_DL - losses_margins + Rxant_gain_DL - Rxsens_DL 
                    l = MAPL_DL
                    
                    a = (1.1 * math.log10(frequency) - 0.7) * H_UE - (1.56 * math.log10(frequency) - 0.8)
                    log_R = (l - 46.3 - 33.9 *math.log10(frequency) + 13.82 * math.log10(H_bs) + a) / (44.9 - 6.55 * math.log10(H_bs))
                    
                    R_DL = 10 ** log_R  # Site radius in kilometers
                    A_site_DL = 1.94 * R_DL ** 2  # Area covered per site in km²
                    N_DL = math.ceil(total_area / A_site_DL)  # Number of sites required

                    return MAPL_DL, R_DL, A_site_DL, N_DL


                # 3- MAPL Calculation for UL
                def UL_Calculations(H_UE, H_bs, total_area):

                    MAPL_UL = Txpwr_UL - feeder_loss + Txant_gain_UL - losses_margins + Rxant_gain_UL - Rxsens_UL 
                    l = MAPL_UL
                    
                    a = (1.1 * math.log10(frequency) - 0.7) * H_UE - (1.56 * math.log10(frequency) - 0.8)
                    log_R = (l - 46.3 - 33.9 *math.log10(frequency) + 13.82 * math.log10(H_bs) + a) / (44.9 - 6.55 * math.log10(H_bs))
                    
                    R_UL = 10 ** log_R  # Site radius in kilometers
                    A_site_UL = 1.94 * R_UL ** 2  # Area covered per site in km²
                    N_UL = math.ceil(total_area / A_site_UL)  # Number of sites required

                    return MAPL_UL, R_UL, A_site_UL, N_UL


            MAPL_DL, R_DL, A_site_DL, N_DL = DL_Calculations(H_UE, H_bs, total_area)
            MAPL_UL, R_UL, A_site_UL, N_UL = UL_Calculations(H_UE, H_bs, total_area)


            return render_template("4G_form_B.html", total_area = total_area, R_DL = R_DL, R_UL =R_UL,  A_site_DL = A_site_DL, A_site_UL = A_site_UL, N_DL = N_DL, N_UL = N_UL, MAPL_DL = MAPL_DL, MAPL_UL = MAPL_UL)


        except Exception as e:
            return f"Error Occurred: {e}"

    return render_template("4G_form_B.html")  # for GET




#Capacity_5G_Calculations
@app.route("/5G_form_A.html", methods =["POST", "GET"])
def cap_5G():
    if request.method == "POST":
        try:

            No_cells_site = int(request.form["No_cells_site"]) 
            Q = float(request.form["Q"]) /100

            #for T_cell
            No_carriers = int(request.form["No_carriers"])
            scaling_factor = int(request.form["scaling_factor"]) 
            NRBs = int(request.form["NRBs"])
            No_slots_sec = int(request.form["No_slots_sec"])
            type_CP = request.form["type_CP"].title()
            type_mod = request.form["type_mod"].upper()
            coding_rate = float(request.form["coding_rate"]) 
            CCH = float(request.form["CCH"]) /100
            No_layers = int(request.form["No_layers"])

            #For TDD
            DL_ratio = float(request.form["DL_ratio"])

            # for calculation of busy hour active users
            Population = int(request.form["Population"])
            mobile_pent = float(request.form["mobile_pent"]) /100
            market_sh = float(request.form["market_sh"]) /100
            BHAU = float(request.form["BHAU"]) /100
            BLER = float(request.form["BLER"]) / 100

            #for voice calls
            voice_call = float(request.form["voice_call"]) /100 
            session_bearer_VC = float(request.form["session_bearer_VC"])  / 1000 
            session_time_VC = float(request.form["session_time_VC"]) 
            duty_ratio_VC = float(request.form["duty_ratio_VC"]) / 100

            #for browsing
            browsing = float(request.form["browsing"]) /100
            session_bearer_brow = float(request.form["session_bearer_brow"]) / 1000  
            session_time_brow = float(request.form["session_time_brow"]) 
            duty_ratio_brow = float(request.form["duty_ratio_brow"]) / 100

            #for gaming
            gaming = float(request.form["gaming"]) /100
            session_bearer_gam = float(request.form["session_bearer_gam"])  / 1000 
            session_time_gam = float(request.form["session_time_gam"])
            duty_ratio_gam = float(request.form["duty_ratio_gam"]) / 100

            #for streaming
            streaming = float(request.form["streaming"]) /100
            session_bearer_strem = float(request.form["session_bearer_strem"])  / 1000 
            session_time_strem = float(request.form["session_time_strem"])
            duty_ratio_strem = float(request.form["duty_ratio_strem"]) / 100


            ####CALCULATIONS
            No_RB_sec = NRBs * No_slots_sec

            #for modulation order & coding rate

            mod_types = {
                "BPSK": 1,
                "QPSK": 2,
                "16QAM": 4,
                "64QAM": 6,
                "256QAM": 8
            }

            No_bits_symbol = mod_types[type_mod]


            #for cycle prefix

            if type_CP == "Normal":
                No_RE_RB = 12 * 14

            elif type_CP == "Extended":
                No_RE_RB = 12 * 12

            #depends on => traffic & redundancy

            No_active_users = Population * mobile_pent * market_sh * BHAU   #active users

            #session traffic voice

            def session_traffic_voice(No_active_users, session_bearer_VC, session_time_VC, duty_ratio_VC, BLER, voice_call):

                session_traffic = session_bearer_VC * session_time_VC * duty_ratio_VC / (1 - BLER)

                total_traffic_VC = voice_call * No_active_users *  session_traffic

                return total_traffic_VC


            #session traffic browsing

            def session_traffic_browsing(No_active_users, session_bearer_brow, session_time_brow, duty_ratio_brow, BLER, browsing):

                session_traffic = session_bearer_brow * session_time_brow * duty_ratio_brow / (1 - BLER)

                total_traffic_brow = browsing * No_active_users * session_traffic

                return total_traffic_brow


            #session traffic gaming

            def session_traffic_gaming(No_active_users, session_bearer_gam, session_time_gam, duty_ratio_gam, BLER, gaming):

                session_traffic = session_bearer_gam * session_time_gam * duty_ratio_gam / (1 - BLER)

                total_traffic_gam = gaming * No_active_users * session_traffic

                return total_traffic_gam


            #session_traffic_streaming

            def session_traffic_streaming(No_active_users, session_bearer_strem, session_time_strem, duty_ratio_strem, BLER, streaming):

                session_traffic = session_bearer_strem * session_time_strem * duty_ratio_strem / (1 - BLER)

                total_traffic_strem = streaming * No_active_users * session_traffic

                return total_traffic_strem



            A = session_traffic_voice(No_active_users, session_bearer_VC, session_time_VC, duty_ratio_VC, BLER, voice_call)

            B = session_traffic_browsing(No_active_users, session_bearer_brow, session_time_brow, duty_ratio_brow, BLER, browsing)

            C = session_traffic_gaming(No_active_users, session_bearer_gam, session_time_gam, duty_ratio_gam, BLER, gaming)

            D = session_traffic_streaming(No_active_users, session_bearer_strem, session_time_strem, duty_ratio_strem, BLER, streaming)

            total_traffic_area =  (A + B + C + D) / 3600


            #FDD 

            def FDD_calc(No_carriers, No_layers, scaling_factor, No_RB_sec,  No_RE_RB, coding_rate, No_bits_symbol, CCH, No_cells_site):

                T_cell = 10**-6 * No_carriers * No_layers * scaling_factor * No_RB_sec * No_RE_RB * No_bits_symbol * coding_rate * (1 - CCH)    #to be in MHz

                T_site = T_cell * No_cells_site * Q     #in MHz

                return T_site


            site_traffic_fdd = FDD_calc(No_carriers, No_layers, scaling_factor, No_RB_sec,  No_RE_RB, coding_rate, No_bits_symbol, CCH, No_cells_site)

            N_fdd = math.ceil(total_traffic_area / site_traffic_fdd) 


            #TDD
            def TDD_calc(No_carriers, No_layers, scaling_factor, No_RB_sec,  No_RE_RB, coding_rate, No_bits_symbol, CCH, No_cells_site):

                T_cell = 10**-6 * No_carriers * No_layers * scaling_factor * No_RB_sec * No_RE_RB * No_bits_symbol * coding_rate * (1 - CCH)    #to be in MHz

                T_site = T_cell * No_cells_site * Q  * DL_ratio   #in MHz

                return T_site


            site_traffic_tdd = TDD_calc(No_carriers, No_layers, scaling_factor, No_RB_sec,  No_RE_RB, coding_rate, No_bits_symbol, CCH, No_cells_site)

            N_tdd = math.ceil(total_traffic_area / site_traffic_tdd) 

            return render_template("5G_form_A.html", total_traffic_area = total_traffic_area , site_traffic_fdd = site_traffic_fdd, site_traffic_tdd = site_traffic_tdd, N_fdd = N_fdd, N_tdd = N_tdd)
        

        except Exception as e:
            return f"Error Occured: {e}" 

    return render_template("5G_form_A.html")



#Coverage_5G_Calculations  
@app.route("/5G_form_B.html", methods = ["POST", "GET"]) 
def cov_5G():
    if request.method == "POST":

        try:
            total_area = float(request.form["total_area"]) * 10**6
            Txpwr_DL = float(request.form["Txpwr_DL"])
            Tx_ant_gain_DL = int(request.form["Tx_ant_gain_DL"])
            Rx_ant_gain_DL = int(request.form["Rx_ant_gain_DL"])
            SINR_DL = float(request.form["SINR_DL"])
            Im_DL = int(request.form["Im_DL"])

            #DATA FOR UL
            Txpwr_UL = int(request.form["Txpwr_UL"])
            Tx_ant_gain_UL = int(request.form["Tx_ant_gain_UL"])
            Rx_ant_gain_UL = int(request.form["Rx_ant_gain_UL"]) 
            SINR_UL = float(request.form["SINR_UL"])
            Im_UL = int(request.form["Im_UL"])

            #common data
            UE_NF = int(request.form["UE_NF"])
            gNB_NF = int(request.form["gNB_NF"])
            frequency = float(request.form["frequency"])   
            BW = int(request.form["BW"])

            #losses
            gNB_cable_loss = float(request.form["gNB_cable_loss"])
            penetration_loss = float(request.form["penetration_loss"])
            foliage_loss = float(request.form["foliage_loss"])
            body_loss = float(request.form["body_loss"])
            rain_fading = float(request.form["rain_fading"])
            slow_fading_margin = float(request.form["slow_fading_margin"])


            ##CALCULATIONS

            ###For Dl => UE senstivity
            Rxsens_DL = -174 + 10 * math.log10(BW * 10**6) + UE_NF + SINR_DL
            # print(f"Rxsens_DL: {Rxsens_DL: .4f}")

            ###For UL => eNB senstivity
            Rxsens_UL = -174 + 10 * math.log10(2 * 720 * 10**3) + gNB_NF + SINR_UL
            # print(f"Rxsens_UL: {Rxsens_UL: .4f}")



            def MAPL_DL(Txpwr_DL, Tx_ant_gain_DL, Rx_ant_gain_DL, body_loss, penetration_loss, slow_fading_margin, gNB_cable_loss, foliage_loss, rain_fading, Im_DL, Rxsens_DL):


                MAPL_DL = (Txpwr_DL + Tx_ant_gain_DL - gNB_cable_loss - penetration_loss - foliage_loss - body_loss - Im_DL - rain_fading - slow_fading_margin + Rx_ant_gain_DL - Rxsens_DL)

                PL = MAPL_DL
                R_DL = 10 ** ((PL - 28 - 20 * math.log10(frequency)) / 22)
                

                A_site_DL = 1.94 * R_DL**2
                N_DL = math.ceil(total_area / A_site_DL)

                return R_DL, MAPL_DL, N_DL, A_site_DL
            
            R_DL, MAPL_DL, N_DL, A_site_DL = MAPL_DL(Txpwr_DL, Tx_ant_gain_DL, Rx_ant_gain_DL, body_loss, penetration_loss, slow_fading_margin, gNB_cable_loss, foliage_loss, rain_fading, Im_DL, Rxsens_DL)



            def MAPL_UL(Txpwr_UL, Tx_ant_gain_UL, Rx_ant_gain_UL, body_loss, penetration_loss, slow_fading_margin, gNB_cable_loss, foliage_loss, rain_fading, Im_UL, Rxsens_UL):


                MAPL_UL = (Txpwr_UL + Tx_ant_gain_UL - gNB_cable_loss - penetration_loss - foliage_loss - body_loss - Im_UL - rain_fading - slow_fading_margin + Rx_ant_gain_UL - Rxsens_UL)

                PL = MAPL_UL
                R_UL = 10 ** ((PL - 28 - 20 * math.log10(frequency)) / 22)


                A_site_UL = 1.94 * R_UL**2
                N_UL = math.ceil(total_area / A_site_UL)

                return MAPL_UL, R_UL, N_UL, A_site_UL
            
            R_UL, MAPL_UL, N_UL, A_site_UL = MAPL_UL(Txpwr_UL, Tx_ant_gain_UL, Rx_ant_gain_UL, body_loss, penetration_loss, slow_fading_margin, gNB_cable_loss, foliage_loss, rain_fading, Im_UL, Rxsens_UL)

            
        except Exception as e:
            return f"Error Occured {e}" 

        return render_template("5G_form_B.html", MAPL_DL = MAPL_DL, MAPL_UL = MAPL_UL, R_DL = R_DL, R_UL = R_UL, A_site_DL = A_site_DL, A_site_UL = A_site_UL, N_DL = N_DL, N_UL = N_UL)

    return render_template("5G_form_B.html")


if __name__ == "__main__":
    app.run(debug=True)
