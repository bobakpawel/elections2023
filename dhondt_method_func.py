import pandas as pd 

#### VARIABLES TO BE SET ####

file_adress = 'C:/badania/wgrane/kandydaci_sejm_2023.csv' ### specify the file path on your local hard drive (file should be downloaded from the PKW www: https://wybory.gov.pl/sejmsenat2023/data/csv/kandydaci_sejm_csv.zip (19.10.2023))
columns_to_import = ['OkregId', 'ListaId', 'NazwaKomitetu', 'Glosy', 'IsMandat'] ### Column names should exactly match the function's parameter names (modify the column names in the file 'Nr okręgu' - 'ListaId', 'Nr listy' - 'ListaId', 'Pozycja na liście' - 'PozycjaNaLiscie', 'Nazwa komitetu' - 'NazwaKomitetu', 'Liczba głosów' - 'Glosy')
oposition_parties_ids_list = [2,3,6] ### provide a list of opposition parties IDs 
pis_id = 4 ### provide PRAWO I SPRAWIEDLIWOSC ID number
konf_id = 5 ### provide KONFEDERACJA ID number

#### END OF SETTING VARIABLES ####

election_results_file = pd.read_csv(file_adress, encoding = 'cp1250', sep = ';', usecols = columns_to_import)
election_results_grouped = election_results_file.groupby(['OkregId', 'ListaId', 'NazwaKomitetu'])[['Glosy', 'IsMandat']].sum().reset_index()   #Group the data by party and district to analyze the scores for each party, rather than individual candidates.

def votes_disposer(df = election_results_grouped, sim = None, opp_index = None):    
    
    if sim == 1 and opp_index == None:
        raise ValueError("When simulating opposition parties (sim = 1), use 'opp_index' as a required parameter for the 'votes_disposer' function. Call it with 'votes_disposer(df, sim, opp_index).")   #Raising an error is crucial to prevent potential issues during function execution.
    
    if (sim != 1 and opp_index != None) or ((sim != 1 and sim != None) and opp_index == None):
        print("When sim != 1, you can skip using sim and opp_index parameters, as they won't affect the function.")   #The function will execute, so there's no need for an error, but providing feedback is a good practice.
    
    parties_and_mandates = df.groupby('NazwaKomitetu')[['Glosy','IsMandat']].sum().reset_index()
    parties_and_mandates_main = parties_and_mandates[parties_and_mandates['IsMandat'] > 1]   #The condition to be met is that the value should be greater than one ('>1') to exclude the 'Mniejszość Niemiecka' group (which is not a guaranteed mandate, but just in case)
    parties_and_mandates_main = parties_and_mandates_main.rename(columns={'Glosy': 'Glosy_winner', 'IsMandat': 'IsMandat_winner'}) #Rename column names to avoid the need for usage of suffixes parameter later.
    
    election_results_combined = df.merge(right = parties_and_mandates_main, on = 'NazwaKomitetu', how = 'inner').filter(items=df.columns) #An approach to exclude parties that have received fewer than two mandates.
    election_results_combined.sort_values(by=['OkregId','ListaId'], inplace = True)
    election_results_combined.insert(4, 'IsOpozycja', election_results_combined.apply(lambda row: 'ZJEDNOCZONA OPOZYCJA' if row['ListaId'] in oposition_parties_ids_list else row['NazwaKomitetu'], axis=1))   #This functionality is essential for future simulations and aggregating opposition parties. The function assigns the value 'Zjednoczona Opozycja' if the analyzed party ID is within the previously formed list of opposition party IDs. Otherwise, party names remain unchanged (e.g., PIS, KONFEDERACJA).
    
    district_votes_mandates = election_results_combined.groupby('OkregId')[['Glosy', 'IsMandat']].sum().reset_index() #The code needs to collect the number of votes and available mandates in each analyzed district (41 rows) for later application of the D'Hondt method calculations.
    district_votes_mandates.rename(columns = {'Glosy' : 'VotesSum', 'IsMandat' : 'MandatesSum'}, inplace = True) 
    election_results_edited = election_results_combined.merge(right = district_votes_mandates, on = 'OkregId', how = 'inner') #Through this merge operation, we will have a single dataframe containing all the necessary data for our mandate distribution calculations, including the potential simulation of an alliance among opposition parties.

    if sim == 1:
        election_results_edited['ListaId'] = election_results_edited['ListaId'].apply(lambda x : 1 if x in oposition_parties_ids_list else 2 if x == pis_id else 3 if x == konf_id else 0) #Setting new IDs for the parties is only required when analyzing the scenario where opposition parties' votes are combined; otherwise, the 'if' lines in the code will be skipped. Opposition parties now receive an ID of 1, while PIS is assigned 2, and KONFEDERACJA gets 3.
        election_results_edited = election_results_edited.groupby(['OkregId', 'ListaId', 'IsOpozycja', 'VotesSum', 'MandatesSum'])['Glosy'].sum().to_frame().reset_index() #Skips the 'NazwaKomitetu' column, which will be recreated shortly. Grouping parties by their 'ListaId' and 'OkregId' means that opposition parties (KO, Trzecia Droga, Lewica) are now aggregated together, and they cannot be seen separately from this point onward.
        election_results_edited['Glosy']= election_results_edited.apply(lambda row: round(row['Glosy'] * opp_index,0) if row['ListaId'] == 1 else row['Glosy'], axis = 1) #This line of code applies the modifier to opposition parties' votes, considering whether the 'join opposition parties' flag will increase or decrease their votes (if it even would)
        election_results_edited.rename(columns = {'IsOpozycja' : 'NazwaKomitetu'}, inplace = True) #The column name used to identify the party is once again 'NazwaKomitetu'.
        
    elected_parties_list = list(set(election_results_edited['NazwaKomitetu']))  #The list of party names and the number of parties are both required, as indicated in the line of code below.
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

    final_election_score_df = pd.DataFrame(final_election_score.items(), columns=['Party', 'No_Mandates']) #Converting the dictionary into a more user-friendly dataframe for easier analysis or export to Excel.

    return final_election_score_df

votes_disposer(election_results_grouped) #Actual mandates distribution in the last election.
votes_disposer(election_results_grouped,1,0.95) #Scenario of joined opposition parties participating in the election and losing 5 percentage points of votes ('Glosy') in every district.
