import pandas as pd 

#### VARIABLES TO BE SET ####

file_adress = 'C:/badania/wgrane/kandydaci_sejm_2023.csv' ### provide your file path from your local hard drive
columns_to_import = ['OkregId', 'ListaId', 'NazwaKomitetu', 'Glosy','IsMandat'] ### The function names must exactly match the column names used within the function

#### END OF SETTING VARIABLES ####

election_results_file = pd.read_csv(file_adress, encoding = 'cp1250', sep = ';', usecols = columns_to_import)
election_results_grouped = election_results_file.groupby(['OkregId', 'ListaId', 'NazwaKomitetu'])[['Glosy', 'IsMandat']].sum().reset_index()

def dhondt_simulator(df = election_results_grouped, add_votes = 1000, considered_party_id = 1):
    
    parties_and_mandates = df.groupby('NazwaKomitetu')[['Glosy','IsMandat']].sum().reset_index()
    parties_and_mandates_main = parties_and_mandates[parties_and_mandates['IsMandat'] > 1]   #one condition needs to be met: it should be greater than one ('>1') to exclude the 'Mniejszość Niemiecka' group.
    parties_and_mandates_main = parties_and_mandates_main.rename(columns={'Glosy': 'Glosy_winner', 'IsMandat': 'IsMandat_winner'})

    election_results_combined = df.merge(right = parties_and_mandates_main, on = 'NazwaKomitetu', how = 'inner').filter(items=election_results_grouped.columns) ###An approach to exclude parties that haven't received more than one mandate.
    election_results_combined.sort_values(by=['OkregId','ListaId'], inplace = True)

    district_votes_mandates = election_results_combined.groupby('OkregId')[['Glosy', 'IsMandat']].sum().reset_index() ### Require the number of votes and the available mandates in each district to apply the D'Hondt method later.
    district_votes_mandates.rename(columns = {'Glosy' : 'VotesSum', 'IsMandat' : 'MandatesSum'}, inplace = True) 
    election_results_edited = election_results_combined.merge(right = district_votes_mandates, on = 'OkregId', how = 'inner')

    elected_parties_list = list(set(election_results_edited['NazwaKomitetu']))
    no_elected_parties = len(elected_parties_list)
    election_score_dict = {}

    for district in range(election_results_edited['OkregId'].nunique()):
        current_district_frame = election_results_edited[election_results_edited['OkregId'] == (district + 1)]  ### Creating a dedicated Data Frame for the current district, inspected during each iteration.
        mandates_in_district = current_district_frame.loc[no_elected_parties*district, 'MandatesSum']   ### Identifying the number of the available mandates in the inspected district.
        dhondt_consideration = []  
    
        for party in elected_parties_list:
            no_of_votes = current_district_frame[current_district_frame['NazwaKomitetu'] == party]['Glosy'].iloc[0]  ### Obtaining the number of votes received by the inspected party in the dedicated district.
            for iter in range(mandates_in_district):
                dhondt_consideration.append((round(no_of_votes / (iter+1),2), party))   ### The core of the D'Hondt method involves adding the party's name and the number of votes divided by 1, then by 2, then by 3, and so on in each iteration. The result of each division is the first element in a tuple (for ease of sorting), while the party name is the second element in the tuple. These tuples are added to a list.
    
        dhondt_consideration = sorted(dhondt_consideration, key = lambda x : x[0], reverse = True)   ### The list needs to be sorted so that the top positions are occupied by parties with the highest vote counts or votes divided by the iteration count.
        dhondt_consideration = dhondt_consideration[:mandates_in_district]  
        dhondt_choice = []    
        
        for entry in dhondt_consideration:
            dhondt_choice.append(entry[1])
        
        district_score = {}
    
        for party in dhondt_choice:          ### Constructing a dictionary using a for loop. If a party is not already in the dictionary, assign it a value of 1 (representing 1 mandate). If the party is already in the dictionary, increment its value by 1.
            if party not in district_score:
                district_score[party] = 1
            else:
                district_score[party] += 1

        election_score_dict[(district+1)] = district_score   #### Creating a specialized dictionary with keys representing district numbers and values containing dictionaries of parties and their respective mandates in that specific district.
        
    final_election_score = {}
    
    for district in election_score_dict:    #### Building a dictionary in a manner similar to the one mentioned above. If a party is not already present in the dictionary, assign it a value equal to its mandates in the currently analyzed district. If the party is already in the dictionary, increment its value by the number of mandates it has in that district.
        for party in election_score_dict[district]:
            if party not in final_election_score:
                final_election_score[party] = election_score_dict[district][party]
            else:
                final_election_score[party] += election_score_dict[district][party]

    final_election_score_df = pd.DataFrame(final_election_score.items(), columns=['Party', 'No_Mandates']) 

    election_simulations = election_results_edited.copy()
    election_simulations['Glosy'] = election_simulations.apply(lambda row : row['Glosy'] + add_votes if row['ListaId'] == considered_party_id else row['Glosy'], axis=1)
    election_sim_dict = {}
 
    for district in range(election_simulations['OkregId'].nunique()):
        current_district_frame = election_simulations[election_simulations['OkregId'] == (district + 1)]
        mandates_in_district = current_district_frame.loc[no_elected_parties*district, 'MandatesSum']
        dhondt_simulation = [] 
        
        for party in elected_parties_list:
            no_of_votes = current_district_frame[current_district_frame['NazwaKomitetu'] == party]['Glosy'].iloc[0]
            for iter in range(mandates_in_district):
                dhondt_simulation.append((round(no_of_votes / (iter+1),2), party))

        dhondt_simulation = sorted(dhondt_simulation, key = lambda x : x[0], reverse = True)  
        dhondt_simulation = dhondt_simulation[:mandates_in_district]  
        dhondt_choice_sim = []    
        
        for entry in dhondt_simulation:
            dhondt_choice_sim.append(entry[1])

        district_score_sim = {}
    
        for party in dhondt_choice_sim:          
            if party not in district_score_sim:
                district_score_sim[party] = 1
            else:
                district_score_sim[party] += 1

        election_sim_dict[(district+1)] = district_score_sim   

    sim_election_score = {}
    
    for district in election_sim_dict:  
        for party in election_sim_dict[district]:
            if party not in sim_election_score:
                sim_election_score[party] = election_sim_dict[district][party]
            else:
                sim_election_score[party] += election_sim_dict[district][party]

    election_sim_final_df = pd.DataFrame(sim_election_score.items(), columns=['Party', 'No_Mandates']) 
    
    analyzed_party_name = election_simulations[election_simulations['ListaId'] == considered_party_id]['NazwaKomitetu'].unique()[0]
    final_party_score = final_election_score_df[election_sim_final_df['Party'] == analyzed_party_name]['No_Mandates'].iloc[0]
    sim_party_score = election_sim_final_df[election_sim_final_df['Party'] == analyzed_party_name]['No_Mandates'].iloc[0]
    trophies_districts = []
    
    if sim_party_score > final_party_score:
        
        for district in range(election_simulations['OkregId'].nunique()):
            try:
                if election_sim_dict[district+1][analyzed_party_name] - election_score_dict[district+1][analyzed_party_name] > 0:
                    trophies_districts.append(district+1)
                else:
                    continue
            except:
                    try:
                        if election_sim_dict[district+1][analyzed_party_name]:
                            trophies_districts.append(district+1)
                    except:
                        continue
                    
            
        districts_string = ''
        for district in range(len(trophies_districts)):
            districts_string += str(trophies_districts[district]) + ', '
        
        districts_string = districts_string[0:-2]
        
        if len(trophies_districts) > 1:
            comm = 'Zwiększenie liczby głosów o ' + str(add_votes) + ' w każdym z 41 okręgów dla partii: ' + analyzed_party_name + ' powoduje dodatkowy uzysk ' + str(len(trophies_districts)) + ' mandatów. Dodatkowe mandaty zdobyto w okręgach: ' + districts_string + '.'
        else:
            comm = 'Zwiększenie liczby głosów o ' + str(add_votes) + ' w każdym z 41 okręgów dla partii: ' + analyzed_party_name + ' powoduje dodatkowy uzysk jednego mandatu. Dodatkowy mandat zdobyto w okręgu: ' + districts_string + '.'
        
        return comm
    
    else:
        comm = 'Zwiększenie liczby głosów o ' + str(add_votes) + ' w każdym z 41 okręgów dla partii: ' + analyzed_party_name + ' nie powoduje zwiększenia liczby mandatów, jakie ta partia uzyskała.'
        return comm

