import pandas as pd 

#### VARIABLES TO BE SET ####

file_adress = 'C:/folder/folder/file_name.csv' #Specify the file path on your local hard drive (file should be downloaded from the PKW www: https://wybory.gov.pl/sejmsenat2023/data/csv/kandydaci_sejm_csv.zip (19.10.2023))
columns_to_import = ['OkregId', 'ListaId', 'NazwaKomitetu', 'Glosy','IsMandat'] #Column names should exactly match the function's parameter names (modify the column names in the file 'Nr okręgu' - 'OkregId', 'Nr listy' - 'ListaId', 'Nazwa komitetu' - 'NazwaKomitetu', 'Liczba głosów' - 'Glosy')

#### END OF SETTING VARIABLES ####

election_results_file = pd.read_csv(file_adress, encoding = 'cp1250', sep = ';', usecols = columns_to_import)
election_results_grouped = election_results_file.groupby(['OkregId', 'ListaId', 'NazwaKomitetu'])[['Glosy', 'IsMandat']].sum().reset_index() #Group the data by party and district to analyze the scores for each party, rather than individual candidates.

def dhondt_simulator(df = election_results_grouped, add_votes = 1000, considered_party_id = 2):
    
    if add_votes == None:
        raise ValueError("This function was designed to add a specified number of votes to a selected party in each of the 41 election districts. Its purpose is to verify whether providing such a bonus will lead to the party gaining additional mandates. Running this function without providing the add_votes parameter serves no purpose.")   #Raising an error is crucial to prevent potential issues during function execution.
    if not isinstance(add_votes, int) or add_votes <= 0:
        raise ValueError("The 'add_votes' parameter must be a positive integer to add votes to the selected party.") #Work only if add_votes parameter is integer and higher than 0.
    if considered_party_id not in [2,3,4,5,6]:
        raise ValueError("The considered_party_id parameter must have one of the following five values: 2 (Trzecia Droga), 3 (Nowa Lewica), 4 (PIS), 5 (KONFEDERACJA) or 6 (Koalicja Obywatelska)")   #Raising an error is crucial to prevent potential issues during function execution.
    
    parties_and_mandates = df.groupby('NazwaKomitetu')[['Glosy','IsMandat']].sum().reset_index()
    parties_and_mandates_main = parties_and_mandates[parties_and_mandates['IsMandat'] > 1]   #The condition to be met is that the value should be greater than one ('>1') to exclude the 'Mniejszość Niemiecka' group (which is not a guaranteed mandate, but just in case)
    parties_and_mandates_main = parties_and_mandates_main.rename(columns={'Glosy': 'Glosy_winner', 'IsMandat': 'IsMandat_winner'}) #Rename column names to avoid the need for usage of suffixes parameter later.

    election_results_combined = df.merge(right = parties_and_mandates_main, on = 'NazwaKomitetu', how = 'inner').filter(items=election_results_grouped.columns) #An approach to exclude parties that have received fewer than two mandates.
    election_results_combined.sort_values(by=['OkregId','ListaId'], inplace = True)

    district_votes_mandates = election_results_combined.groupby('OkregId')[['Glosy', 'IsMandat']].sum().reset_index() #The code needs to collect the number of votes and available mandates in each analyzed district (41 rows) for later application of the D'Hondt method calculations.
    district_votes_mandates.rename(columns = {'Glosy' : 'VotesSum', 'IsMandat' : 'MandatesSum'}, inplace = True) 
    election_results_edited = election_results_combined.merge(right = district_votes_mandates, on = 'OkregId', how = 'inner') #Through this merge operation, we will have a single dataframe containing all the necessary data for our mandate distribution calculations, including the potential simulation of an alliance among opposition parties.

    elected_parties_list = list(set(election_results_edited['NazwaKomitetu'])) #The list of party names and the number of parties are both required, as indicated in the line of code below.
    no_elected_parties = len(elected_parties_list)
    election_score_dict = {}

    for district in range(election_results_edited['OkregId'].nunique()): #Creating a 'for' loop that will iterate once for each of the 41 election districts.
        current_district_frame = election_results_edited[election_results_edited['OkregId'] == (district + 1)]  #Creating a dedicated DataFrame for the current district by adding 1 to match the iteration starting from 0 with 'OkregId' starting from 1. Each iteration analyzes a DataFrame consisting of 5 rows (or 3 in the case of analyzing joined opposition parties).
        mandates_in_district = current_district_frame.loc[no_elected_parties*district, 'MandatesSum']   #Identifying the number of available mandates in the inspected district using the 'loc' function, based on the 'MandatesSum' column and a row calculated during each iteration. For the first iteration, the row number is 5 (or 3 in case of joined opposition) times the district number (e.g., 0 for the 1st iteration), and it increases accordingly in subsequent iterations. For the 10th iteration, the row number would be 5 (or 3 in case of joined opposition) times the district number, which is 5 * 10 = 50.
        dhondt_consideration = []  
    
        for party in elected_parties_list: #So for every district (the ongoing iteration), there will be another iteration for every analyzed party.
            no_of_votes = current_district_frame[current_district_frame['NazwaKomitetu'] == party]['Glosy'].iloc[0]  #Obtaining the number of votes received by the inspected party in the dedicated district using the 'iloc' function.
            for iter in range(mandates_in_district):
                dhondt_consideration.append((round(no_of_votes / (iter+1),2), party))   #The essence of the D'Hondt method is to calculate a series of values for each party, consisting of the party's name and the number of votes divided by 1, 2, 3 (iter + 1), and so on in each iteration. These pairs, represented as tuples, are added to a list for sorting.
        
        dhondt_consideration = sorted(dhondt_consideration, key = lambda x : x[0], reverse = True)   #The list is sorted to place parties with the highest vote counts or votes divided by the iteration count at the top positions.
        dhondt_consideration = dhondt_consideration[:mandates_in_district]  #The list is trimmed to contain the same number of elements as the number of mandates to be allocated.
        dhondt_choice = []    
          
        for entry in dhondt_consideration: #The list still consists of tuples (number of votes or divided votes, party name). To allocate mandates in districts, a 'for' loop is used to add elements (the second element of each tuple which is a party name) to a newly created list.
            dhondt_choice.append(entry[1])

        district_score = {}
        
        for party in dhondt_choice:          #Constructing a dictionary using a 'for' loop. If a party is not already in the dictionary, it is assigned a value of 1 (representing 1 mandate). If the party is already in the dictionary, its value is incremented by 1.
            if party not in district_score:
                district_score[party] = 1
            else:
                district_score[party] += 1

        election_score_dict[(district+1)] = district_score   #Creating a specialized dictionary with keys representing district numbers and values containing dictionaries of parties and their respective mandates in that specific district.
    
    final_election_score = {}
    
    for district in election_score_dict:    #Building a dictionary in a manner similar to the one mentioned above. If a party is not already present in the dictionary, it is assigned a value equal to its mandates in the currently analyzed district. If the party is already in the dictionary, its value is incremented by the number of mandates it has in that district. This way, mandates for all the parties across the entire country are assigned.
        for party in election_score_dict[district]:
            if party not in final_election_score:
                final_election_score[party] = election_score_dict[district][party]
            else:
                final_election_score[party] += election_score_dict[district][party]

    final_election_score_df = pd.DataFrame(final_election_score.items(), columns=['Party', 'No_Mandates']) #Transforming the dictionary into a user-friendly dataframe for convenient future comparisons.
    
    election_simulations = election_results_edited.copy() #As the data in dataframe will be modified just in case a safe copy was prepared.
    election_simulations['Glosy'] = election_simulations.apply(lambda row : row['Glosy'] + add_votes if row['ListaId'] == considered_party_id else row['Glosy'], axis=1) #Modifying the 'Glosy' column: If the value in the 'ListaId' column is equal to the considered_party_id parameter, then increase the 'Glosy' value by the amount specified in the add_votes parameter.
    election_sim_dict = {}
 
    for district in range(election_simulations['OkregId'].nunique()):  #The code within that for loop essentially replicates the steps used to calculate mandate distribution without changing the vote counts. While some variable names may vary, the core logic of the code remains consistent. It simply calculates the distribution of new mandates in each district after increasing the vote count for a selected party in each district.
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

    election_sim_final_df = pd.DataFrame(sim_election_score.items(), columns=['Party', 'No_Mandates']) #A newly generated dataframe represents the simulation of mandate distribution after boosting the party with ID (considered_party_id) by x (add_votes) in every district. This dataframe will serve as the foundation for subsequent calculations.

    analyzed_party_name = election_simulations[election_simulations['ListaId'] == considered_party_id]['NazwaKomitetu'].unique()[0] #Assigning the full name of the analyzed party to the variable.
    final_party_score = final_election_score_df[final_election_score_df['Party'] == analyzed_party_name]['No_Mandates'].iloc[0] #Assigning the number of mandates the party received in the actual election process to this variable.
    sim_party_score = election_sim_final_df[election_sim_final_df['Party'] == analyzed_party_name]['No_Mandates'].iloc[0] #Assigning the number of mandates the party received in the simulated election process (after votes manipulation) to this variable.
    trophies_districts = []  
    
    if sim_party_score > final_party_score: #The code within this IF statement will be executed if the party obtains more mandates in the simulation performed by this function than in the real election process.
        
        for district in range(election_simulations['OkregId'].nunique()): #The for loop will iterate for each of the 41 districts.
            try:
                if election_sim_dict[district+1][analyzed_party_name] - election_score_dict[district+1][analyzed_party_name] > 0:   #Accessing the primary simulation (and election) dictionaries to retrieve a dictionary for the specific district. Then, extracting the number of mandates the party received in the analyzed district and comparing the value obtained in the simulation to the real election process.
                    trophies_districts.append(district+1)  #If the number of mandates obtained in the simulation is greater than in the actual election for the analyzed district, the function will append the district number to the 'trophies_districts' list.
                else: #If the number of mandates obtained in the simulation is not greater than the number of mandates received by the party in that district in the real election process, simply proceed to the next district in the iteration.
                    continue   
            except:   #Try/except approach was employed to handle cases where the analyzed party did not receive any mandates in the real election process in the analyzed district but obtained some in the simulation.
                    try:
                        if election_sim_dict[district+1][analyzed_party_name]:
                            trophies_districts.append(district+1)
                    except:
                        continue
                    
        districts_string = '' #The iteration process below appends the district number(s) to the string that will be displayed to the user at the end of the function.
        for district in range(len(trophies_districts)):
            districts_string += str(trophies_districts[district]) + ', ' 
        
        districts_string = districts_string[0:-2] #Removing the comma that appears after the last district, which should not be there.
        
        if len(trophies_districts) > 1: #One message is for a singular communication if the difference is only one mandate across the entire country. Another message is for a plural communication if there are multiple extra mandates.
            comm = 'Increasing the number of votes by ' + str(add_votes) + ' in each of the 41 districts for the party: ' + analyzed_party_name + ' results in an additional gain of mandates in ' + str(len(trophies_districts)) + ' districts. These extra mandates were obtained in districts: ' + districts_string + '.'
        else:
            comm = 'Increasing the number of votes by ' + str(add_votes) + ' in each of the 41 districts for the party: ' + analyzed_party_name + ' results in an additional gain of a mandate in 1 district. That extra mandate was obtained in district: ' + districts_string + '.'
        
        return comm
    
    else:   #If the party secures an identical number of mandates in both the real election process and the simulation performed by this function, return this message.
        comm = 'Increasing the number of votes by ' + str(add_votes) + ' in each of the 41 districts for the party: ' + analyzed_party_name + ' does not result in an increase in the number of mandates that the party has obtained.'
        return comm

