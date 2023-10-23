import pandas as pd 
import numpy as np
import matplotlib as plt
import re #importing libraries: pandas, numpy, matplotlib and re

file_path = 'C:/badania/wgrane/kandydaci_sejm_2023_b.csv'
columns_to_import = ['OkregId', 'ListaId', 'PozycjaNaLiscie', 'NazwaKomitetu',
                     'NazwiskoImiona', 'Glosy', 'ProcentGlosowListy', 'ProcentGlosowOkregu', 'IsMandat']
candidates = pd.read_csv(file_path, encoding='cp1250', sep=';', usecols = columns_to_import) #Loading the file using variables for the file path and columns to import (column names may need to be changed in, for example, Excel, or uploaded here without using the usecol parameter, and then renamed).

candidates_copy = candidates.copy() #The unedited copy of the originally imported data frame object.

elected_parties = candidates.groupby('NazwaKomitetu')['IsMandat'].sum().to_frame().reset_index()
elected_parties.rename(columns = {'IsMandat' : 'PartyMandates'}, inplace = True)
candidates = candidates.merge(right = elected_parties, on = 'NazwaKomitetu', how = 'inner')
candidates = candidates[candidates['PartyMandates'] > 1] #These lines of code are intended to exclude parties (and their candidates) that did not receive any parliamentary mandates. A new dataframe object, 'elected_parties,' was created to group parties and sum the mandates they obtained. Subsequently, this dataframe object was used to perform an inner merge with the original dataframe object 'candidates' to exclude candidates from parties that did not secure any mandates.
del candidates['PartyMandates']     
elected_parties_list = list(elected_parties[elected_parties['PartyMandates'] > 1]['NazwaKomitetu'])

#### LIST LEADERS ANALYSIS ####

candidates[(candidates['ListaId'] == 2) & (candidates['ProcentGlosowListy']>=50)].sort_values(by='ProcentGlosowListy', ascending = False).head(15)
candidates[(candidates['ListaId'] == 5) & (candidates['ProcentGlosowListy']>=50)].sort_values(by='ProcentGlosowListy', ascending = False).head(15)

#1. In each of the analyzed parties that obtained mandates in the recent Polish election, there are leaders who received more than 50% of the votes in their respective districts for their party.
#2. Two groups, Konfederacja and Koalicja Obywatelska, had 12 and 11 leaders, respectively, who received more than 50% of the votes that their respective parties obtained in their districts. Interestingly, despite Konfederacja's dominance, half of these leaders did not secure a parliamentary mandate. However, all 11 Koalicja Obywatelska leaders will have seats in the newly-formed parliament.
#3. The former ruling party, PIS, had 7 such prominent leaders. Interestingly, 4 of them are men, and 3 are women. Six of these leaders, excluding Elżbieta Witek, received over 100,000 votes.
#4. Nowa Lewica had only 4 candidates meeting this criterion, and for Trzecia Droga, there were just two candidates, notably the two most recognizable party leaders: Szymon Hołownia and Władysław Kosiniak-Kamysz. In both of these parties, there are 11-12 candidates who received between 40% and 50% of the votes that their party obtained in the districts.
#5. In the case of Nowa Lewica, all 4 of the previously mentioned leaders are women. Interestingly, the party leader Włodzimierz Czarzasty is not included in that summary. He is the only primary leader of the party who did not secure more than 50% of the party's votes in the district where he ran. His score was 27.3% of Nowa Lewica's votes in District 32.

#### MANDATE WINNERS AND THEIR STARTING POSITIONS ANALYSIS ####

candidates_places = candidates.pivot_table(index = 'PozycjaNaLiscie', columns = 'NazwaKomitetu', values = 'IsMandat', aggfunc = 'sum') #Creating a pivot table that will display the starting positions of mandate-winning candidates in rows, party names in columns, and the count of candidates who won mandates from each party and each starting position in the cells.
candidates_places = candidates_places.replace(0.0, np.NaN).dropna(how='all').fillna(0) #Modifying the table to filter out starting positions that did not result in any mandates in the recent election process and replacing NaN values with 0's.
for party in elected_parties_list:  #A for loop that, in each iteration, generates a dedicated column for a party that has entered the parliament. It calculates the proportion of mandates that the party obtained in each starting position by dividing the number of mandates won by the total number of mandates that the party received in the last parliamentary election.
    candidates_places[party + '_perc'] = round(100 * candidates_places[party] / elected_parties[elected_parties['NazwaKomitetu'] == party]['PartyMandates'].iloc[0],1)  

#1 There is only one candidate from the party Trzecia Droga who received the starting position number 1 and will not have a seat in the new parliament. There is also only one candidate from Trzecia Droga who received the 40th position and secured a mandate. Both of these candidates will be identified with the following line of code, which establishes a filter combination for the analyzed dataframe object.
candidates[(candidates['ListaId'] == 2) & (((candidates['PozycjaNaLiscie'] == 1) & (candidates['IsMandat'] == 0)) | ((candidates['PozycjaNaLiscie'] == 40) & (candidates['IsMandat'] == 1)))]
#2 Almost all future members of parliament from Konfederacja were leaders of their lists in the district, except for one individual. This person will be identified by applying the following three filters to the 'candidates' dataframe.
candidates[(candidates['ListaId'] == 5) & (candidates['PozycjaNaLiscie'] == 2) & (candidates['IsMandat'] == 1)] 
#3 Most of the mandate winners from Nowa Lewica were positioned in the first (or occasionally the second) starting place in their districts, with the exception of two individuals. One was placed 4th, and the other was placed 18th. The code line below will assist in identifying them and further examining their results.
candidates[(candidates['ListaId'] == 3) & ((candidates['PozycjaNaLiscie'] == 4) | (candidates['PozycjaNaLiscie'] == 18)) & (candidates['IsMandat'] == 1)] 
#4 The following line of code identifies 4 candidates from PIS and 3 candidates from KO who received a significant (for their respective parties) second starting position but did not win an election. As for the author, who is not closely following politics, this is their first encounter with these surnames.
candidates[((candidates['ListaId'] == 4) | (candidates['ListaId'] == 6)) & (candidates['PozycjaNaLiscie'] == 2) & (candidates['IsMandat'] == 0)] 
#5 Both parties that obtained the highest number of mandates secured a very similar percentage of mandates received by individuals with starting positions 5 and higher. It was 85.0% for PIS and 86.6% for Koalicja Obywatelska. The code to identify these numbers is provided below.
sum(candidates_places[candidates_places['KOMITET WYBORCZY PRAWO I SPRAWIEDLIWOŚĆ_perc']>=5]['KOMITET WYBORCZY PRAWO I SPRAWIEDLIWOŚĆ_perc'])
sum(candidates_places[candidates_places['KOALICYJNY KOMITET WYBORCZY KOALICJA OBYWATELSKA PO .N IPL ZIELONI_perc']>=5]['KOALICYJNY KOMITET WYBORCZY KOALICJA OBYWATELSKA PO .N IPL ZIELONI_perc'])

#### IN-DEPTH EXAMINATION OF INDIVIDUAL RESULTS ####

heroes_and_losers = candidates.copy() #Generating a copy of a dataframe object as a precaution and best practice (the original dataframe may undergo modifications).
heroes_and_losers['DistrictPartyRnk'] = heroes_and_losers.groupby(['OkregId', 'ListaId'])['Glosy'].rank(ascending = False) #Adding a new column that, using the groupby and rank functions, establishes a ranking of candidates for each party in each district, starting from those who received the highest number of votes (rank 1) to those who received the fewest votes.
heroes_and_losers['Pos_vs_Score_Diff'] = heroes_and_losers['PozycjaNaLiscie'] - heroes_and_losers['DistrictPartyRnk']    #Establishing a column in which we calculate the difference between the candidate's original position on the list and the position they attained, determined by the ranking of votes within their party and electoral district. This column is intended for filtering out candidates with unexpectedly strong (or weaker) performances.
heroes_and_losers.sort_values(by = ['OkregId', 'ListaId', 'PozycjaNaLiscie'], ascending = [True, True, True], inplace = True)
heroes_and_losers['ToIdentifyLastOnes'] = heroes_and_losers.groupby(['OkregId', 'ListaId'])['PozycjaNaLiscie'].rank(ascending=False) #Introducing a new column that ranks individuals in reverse order to their initial positions. This means that the last candidate will be assigned the value '1,' which will be utilized in subsequent analyses.
heroes_and_losers['IsTheLastOne'] = 0  
heroes_and_losers.loc[heroes_and_losers['ToIdentifyLastOnes'] == 1, 'IsTheLastOne'] = 1 #The previous line of code set all rows in that column to '0'. The following line of code assesses whether a candidate is the last one in the list (for their party and electoral district) by verifying if the candidate has a value of '1' in the previously established column: 'ToIdentifyTheLastOnes'. If this condition is satisfied, a value of '1' is assigned. This approach has created a flag column (0/1).
del heroes_and_losers['ToIdentifyLastOnes']   #The column is no longer required and has therefore been deleted.

heroes_and_losers.sort_values(by = 'Pos_vs_Score_Diff', ascending = False, inplace = True)
is_elected = heroes_and_losers['IsMandat'] == 1
votes_more_than_5k = heroes_and_losers['Glosy'] > 5000
last_one_filter = heroes_and_losers['IsTheLastOne'] == 1 #Sorting the values based on a newly created column and establishing filters that will be utilized in subsequent analyses.

#1 By excluding individuals placed in the last positions on the lists (whether this is due to parties strategically assigning stronger candidates or perhaps influenced by some psychological factor, is a question for political scientists or psychologists), we can identify candidates who have achieved significantly higher-ranking positions than initially assigned by their party.
heroes_and_losers[~last_one_filter].head(10) 
#2 Concerning Nowa Lewica, most of the positive observations about that party also relate to women candidates. The TOP10 performers, determined by the difference between the starting position and the final rank based on the number of votes received, are all women. Unfortunately, none of them were elected, and only one of them received more than 2.5k votes. While their individual achievements are noteworthy, they did not make a substantial contribution to the overall party score.
heroes_and_losers[(heroes_and_losers['ListaId'] == 3) & (~last_one_filter)].head(10)
#3 Applying the condition of having received more than 5k votes to the previous line of code results in a significant change. A male candidate, Robert Maslak, finished 8 places higher than his starting position (3 vs. 11). The second most notable difference between the starting position and the position determined by the vote ranking is 'only' 2 places (given the previously mentioned conditions).
heroes_and_losers[(heroes_and_losers['ListaId'] == 3) & (~last_one_filter) & votes_more_than_5k].head(10) 
#4 There are many 'hero' candidates among the Prawo i Sprawiedliwość candidate lists. Nine individuals received more than 5k votes and finished at least 10 places higher than their starting positions. Each of these candidates is undoubtedly worthy of recognition, and while they all have remarkable stories, Maria Kurowska stands out as the only one who secured a parliamentary mandate. An interesting observation is that she was initially assigned a very unfavorable starting position, both in the 2019 election and in the recent parliamentary election. Nevertheless, she managed to secure a mandate on both occasions, which suggests that she might have the potential for an even more favorable starting position in future parliamentary elections.
heroes_and_losers[(heroes_and_losers['ListaId'] == 4) & (~last_one_filter) & votes_more_than_5k].head(10)
#5 'Hero' candidates can also be found among the Koalicja Obywatelska lists. One such candidate is Wojciech Jaskulski, who started with a position of 20 (not the last one in that district) and garnered nearly 7.5k votes, finishing as the fourth-highest ranked KO candidate in that district.
heroes_and_losers[(heroes_and_losers['ListaId'] == 6) & (~last_one_filter) & votes_more_than_5k].head(10) 
#6 This line of code returns candidates who were not placed in the last position on the list, were elected, and finished at least 5 places higher than their starting position. Among these candidates, we can identify members of the previous parliament (2019) who were assigned less favorable starting positions, such as Franciszek Sterczewski, Marcin Porzucek, Norbert Kaczmarczyk, and Łukasz Mejza. Additionally, there are parliament newcomers, such as Rafał Siemaszko and Marcin Józefaciuk, as well as candidates who made a return to parliament, like Marek Jakubiak.
heroes_and_losers[~last_one_filter & is_elected & (heroes_and_losers['Pos_vs_Score_Diff'] >= 5)].head(15)
 
heroes_and_losers.sort_values(by = 'Pos_vs_Score_Diff', ascending = True, inplace = True)
top_3 = heroes_and_losers['PozycjaNaLiscie'] <= 3 
top_10 = heroes_and_losers['PozycjaNaLiscie'] <= 10
last_one_filter = heroes_and_losers['IsTheLastOne'] == 1
is_elected = heroes_and_losers['IsMandat'] == 1

#7 Candidates who finished significantly lower in the ranking (based on the number of votes received in that district within their party) share some common characteristics. They are often candidates starting in positions 8 - 15, received no more than a few hundred votes, and typically represent districts from which 15 or more candidates are elected. This suggests that more candidates also initiate their campaigns in these districts, which mathematically enables/increases the possibility of finishing 15 - 20 places lower than their starting position.
heroes_and_losers.head(10)
#8 Candidates with the TOP3 starting positions were analyzed, and their initial places were compared to the positions they ultimately secured. Each party made a significant error: a candidate placed in the TOP3 who finished 6 - 8 places lower when ranked by the number of votes received in comparison to candidates from the same district and the same party. Nonetheless, it appears that PIS made the most mistakes, with one candidate finishing 8 places lower than his starting position and two more candidates ranked 6 places lower than their initial places. Notably, many PIS candidates who finished significantly lower than their starting position were given the 2nd starting position, while other parties made their biggest errors with candidates who had the 3rd starting position (the author guesses that it may be more understandable to make a mistake with a candidate starting in the 3rd place rather than the 2nd).
heroes_and_losers[top_3].head(10)

#### IN-DEPTH EXAMINATION OF INDIVIDUAL RESULTS (CREATING NEW INDICATORS) ####

# Setting up a new column, "StrengthVSPlace" - this column groups candidates by party ('ListaId') and their starting positions ('PozycjaNaLiscie'). It will be used to calculate the average percentage of the party's votes obtained by candidates who started from a particular position. For example, on average, a PIS candidate who started in the 3rd position garnered 11.26% of PiS votes in the district.
# Setting up a new column, "CandidatePower" - this column divides the real percentage of votes of his party gathered by a candidate in a district by the average percentage of the party's votes obtained by candidates who started from a particular position. So the value above 1.0 means the candidate with x starting place was stronger than the average candidate from his party who had the same starting place. And the value below 1.0 means his result was weaker comparing to his colleagues from the party with the same starting place in other districts. Of course, this metric should not be analyzed alone to determine a candidate's efficiency, as it is possible that he had stronger or weaker competition in his party in his district than colleagues from different districts. Also, parties tend to put their stronger candidates in districts where their performance is better.
heroes_and_losers['StrenghtVSPlace'] = heroes_and_losers.groupby(['ListaId', 'PozycjaNaLiscie'])['ProcentGlosowListy'].transform('mean')
heroes_and_losers['CandidatePower'] = heroes_and_losers['ProcentGlosowListy'] / heroes_and_losers['StrenghtVSPlace']  #### dividing how much percentage score the candidate receive (in his list, in his district) by the parameter StrenghtVSPlace (described above), the lower the value, the weaker the candidate vs comparing to other candidates of that party in theat list, the higher the number the more influential that candidate was
heroes_and_losers.sort_values(by = 'CandidatePower', ascending = False, inplace = True)
last_one_filter = heroes_and_losers['IsTheLastOne'] == 1
votes_more_than_5k = heroes_and_losers['Glosy'] > 5000

#1 This code was executed for candidates from each of the 5 parties with over 5k votes who didn't occupy the last starting list position. A few identified findings: Bogdan Zdrojewski, 4th in KO District 3, secured 29.86% of KO's votes, while the average for 4th place KO candidates was 6.09% (4.86x higher). Dorota Olko (No. 4, District 19, Nowa Lewica) got 19.16% of Nowa Lewica votes, while the average for 4th place Nowa Lewica candidates was 5.06% (3.78x). Both got mandates. Exceptional scores without mandates include Grzegorz Macko from PiS (8.84x better than average for his rank in his party) and Krystian Jarubas from Trzecia Droga (7.23x).
heroes_and_losers[(heroes_and_losers['ListaId'] == 6) & (~last_one_filter) & (votes_more_than_5k)].head() #NL: Dorota Olko, Daria Popiołek, #PIS: Maria Kurowska, Marcin Porzucek, #KO: Bogdan Zdrojewski, Rafał Siemaszko

heroes_and_losers.sort_values(by = 'CandidatePower', ascending = True, inplace = True)
top_3 = heroes_and_losers['PozycjaNaLiscie'] <= 3
leader = heroes_and_losers['PozycjaNaLiscie'] == 1

#2 The comments for the code below are just a sample of findings. The most extreme example is Paweł Wdówik from PIS, who was given the starting place: 3 and gathered 1.22% of PIS votes in that district, while the average value for the 3rd-placed candidates in PIS is 11.26. The CandidatePower index was a record: 0.11. Another extreme case was Urszula Zielińska from KO, who was in the number 2 position and received only 0.96% of KO's votes in her district, while the average value for the second-placed candidates in KO is 14.76%. Her CandidatePower index was 0.15. Interestingly, she still secured the mandate. A mitigating factor for the candidate might be that she started from district 19, which was dominated by party leader Donald Tusk.
heroes_and_losers[top_3 & (heroes_and_losers['ListaId'] == 6)].head()

#3 The code was executed separately for each of the parties, with a focus on investigating the CandidatePower index for the party's main leader(s). Donald Tusk (KO), Jaroslaw Kaczynski & Mateusz Morawiecki (PIS), Szymon Holownia & Wladyslaw Kosiniak-Kamysz (Trzecia Droga), Slawomir Mentzen & Krzysztof Bosak (Konfederacja) achieved indisputably good scores when compared to other list leaders in their parties. Surprisingly, Nowa Lewica leaders Wlodzimierz Czarzasty & Adrian Zandberg finished in the 36th and 35th places among other Nowa Lewica leaders. Wlodzimierz Czarzasty finished in the second place on the Nowa Lewica list in district 32, just behind the candidate placed last on the list, who secured his mandate for the first time: Lukasz Litewka, receiving 81.7% more votes than the main leader of his party. The 13 weakest CandidatePower index scores in Nowa Lewica were achieved by male candidates, while the top 7 scores were achieved by females.
heroes_and_losers[leader & (heroes_and_losers['ListaId'] == 2)] 

#4 #4 The previous point focused on the main party leaders and their very good performance (except Nowa Lewica). However, there were some list leaders who, according to the population's verdict, were placed too high. This is especially true for three leaders of PIS and one leader of Konfederacja. PIS list leaders, Pawel Szrot, Ryszard Terlecki, and Leonard Krasulski, finished 2nd or 3rd in their districts, and their party's vote share in the district was much worse than the average. The average PIS leader gathered 32.04% of the votes, while these three gentlemen achieved only 12-13% of the vote share, resulting in a very low CandidatePower index of 0.388 - 0.413. In the case of Konfederacja, Janusz Korwin-Mikke's result was particularly poor with a CandidatePower index of 0.41 (the next worst Konfederacja leader's score was 0.68).   
heroes_and_losers[leader & (heroes_and_losers['ListaId'] == 2)].head(8)  

#### IS THERE A CANDIDATE WHO GATHERED MORE VOTES THAN THE ENTIRE COMPETING PARTY IN THE SAME DISTRICT? ####

extremals = heroes_and_losers.copy()
extremals.sort_values(by=['OkregId', 'ListaId', 'PozycjaNaLiscie'], ascending = [True, True, True], inplace = True)
extremals['GlosyParOkr'] = extremals.groupby(by = ['NazwaKomitetu', 'OkregId'])['Glosy'].transform(sum) #Groupby instruction to assign values to a newly created column where each row will be filled with the district sum of votes for the party the candidate is representing.
votes_sum_ko = extremals.groupby('OkregId').apply(lambda x: x[x['ListaId'] == 6]['Glosy'].sum())
votes_sum_pis = extremals.groupby('OkregId').apply(lambda x: x[x['ListaId'] == 4]['Glosy'].sum()) #Creating a data series object consisting of 41 elements, one for each district, representing the total number of votes given to PIS (or KO, as mentioned in the previous line of code) in the analyzed district.
extremals['SumaGlosowPis'] = extremals['OkregId'].apply(lambda x: votes_sum_pis[x])
extremals['SumaGlosowKo'] = extremals['OkregId'].apply(lambda x: votes_sum_ko[x]) #Creating two new columns: one containing the number of votes received by PiS in the analyzed district (and the second one is similar but for KO votes). The apply and lambda structures are used here as an index to retrieve the correct value from the data series votes_sum_pis (or votes_sum_ko).
extremals['KoDominator'] = (extremals['Glosy'] > extremals['SumaGlosowPis']).astype(int)
extremals['PisDominator'] = (extremals['Glosy'] > extremals['SumaGlosowKo']).astype(int) #Creating two additional columns that will be populated with a series of values 0/1. This is done after applying the astype(int) function, which converts boolean values to integers. A value of 1 will be assigned if the candidate being analyzed received more votes ('Glosy') than the entire PiS (or KO) party in the same district ('SumaGlosowPis' or 'SumaGlosowKo'). 
extremals[(extremals['PisDominator'] == 1) | (extremals['KoDominator'] == 1)] #Applying a set of filters to the previously copied data frame to identify hero candidates who received more votes than their entire competing party in the same district. In this analysis, four such politicians were identified: Donald Tusk, Adam Szłapka, Jarosław Kaczyński, and Anna Pieczarka. An amazing achievement!

#### STARTING PLACES AND THE PERFORMANCE ####

heroes_and_losers.sort_values(by=['OkregId', 'ListaId', 'PozycjaNaLiscie'], ascending = [True, True, True], inplace = True)


#1 LEADERS: Employing column indexing to extract the two essential columns and then implementing a filter to display only the top-ranking leaders on the list (the StrengthVSPlace metric will maintain the same value regardless of the district being filtered). The list leaders of Konfederacja were, on average, accountable for securing 46.5% of the party's votes in the district, whereas PiS list leaders had the least influence on the final party score, accounting for only 32% of the votes. The leaders of Nowa Lewica and Trzecia Droga achieved remarkably similar scores, with Nowa Lewica at 37.1% and Trzecia Droga at 37.7%. Additionally, the leaders of KO (Koalicja Obywatelska) came close to Konfederacja's result, securing 41.3%.
places_leaders = heroes_and_losers[['NazwaKomitetu', 'StrenghtVSPlace']][(heroes_and_losers['PozycjaNaLiscie'] == 1) & (heroes_and_losers['OkregId'] == 1)]
#2 TOP3: The top three placed leaders had the most significant influence on KO's final election result, collectively garnering an average of 67% of the votes for their party in the analyzed district. In contrast, PiS leaders, with 57.6%, fell almost 10 percentage points lower than KO's top three placed candidates. Similar to the list leaders, the scores achieved by Trzecia Droga and Nowa Lewica were nearly identical, with percentages of 60.41% and 60.48%, respectively.
places_top3 = heroes_and_losers[['NazwaKomitetu', 'StrenghtVSPlace']][(heroes_and_losers['PozycjaNaLiscie'] <= 3) & (heroes_and_losers['OkregId'] == 1)].groupby('NazwaKomitetu')['StrenghtVSPlace'].sum().to_frame()
#3 PLACES 5 - 10: Candidates who were allocated starting positions between 5 and 10 had the most significant impact on PiS results, contributing to 21.37% of this party overall performance. Their influence on other parties' results was remarkably similar: 14.84% for Konfederacja, 15.86% for KO (Koalicja Obywatelska), and, consistent with earlier groups, Nowa Lewica and Trzecia Droga achieved nearly identical scores, with percentages of 16.82% and 16.86%, respectively.
places_5_10 = heroes_and_losers[['NazwaKomitetu', 'StrenghtVSPlace']][(heroes_and_losers['PozycjaNaLiscie'] <= 10) & (heroes_and_losers['PozycjaNaLiscie'] >= 5) & (heroes_and_losers['OkregId'] == 1)].groupby('NazwaKomitetu')['StrenghtVSPlace'].sum().to_frame()
#4 PLACES 10 - 20: Candidates who were positioned between the 10th and 20th starting places had the least influence on the scores of the two winning parties, contributing to 10.6% for KO (Koalicja Obywatelska) and 11.6% for PiS. In this instance, the scores for Nowa Lewica and Trzecia Droga are not identical. On average, candidates from Nowa Lewica with these starting positions secured 18% of the district's votes, while for Trzecia Droga, that value was 16.6%.
places_10_20 = heroes_and_losers[['NazwaKomitetu', 'StrenghtVSPlace']][(heroes_and_losers['PozycjaNaLiscie'] <= 20) & (heroes_and_losers['PozycjaNaLiscie'] >= 10) & (heroes_and_losers['OkregId'] == 1)].groupby('NazwaKomitetu')['StrenghtVSPlace'].sum().to_frame()

#Each of the group's average percentage share in votes in the district can be visually represented on a chart, like the one shown below (commented out for reference):
#places_10_20.plot(kind = 'barh', color = ['b'], xlim = 0.75*(min(places_10_20['StrenghtVSPlace'])), title = 'Chart title')

#### LESS RECOGNIZABLE CANDIDATES WHO SHARE THE SAME SURNAMES AS THE MAIN PARTY LEADERS ####

famous_surnames = ['ZIOBRO', 'KACZYŃSKI', 'TUSK', 'TRZASKOWSKI', 'HOŁOWNIA', 'KORWIN', 'BOSAK']  #Setting a dictionary with surnames of people who are considered as famous/leaders.
general_filter = pd.Series([0] * len(heroes_and_losers)) #Generating a Data Series object with the same length as the data frame 'heroes_and_losers,' where all cells are initially populated with the value 0. This object will be customized and employed as a filter at a later stage.
heroes_and_losers.reset_index(inplace = True)

for surname in famous_surnames:  #Iterating through each surname in the 'famous_surnames' list.
    regex = re.compile('.*' + surname + '.*', re.IGNORECASE)  #Creating a regex expression that will capture a variable 'surname' (representing a surname from the list of famous surnames) and subsequently, after applying a filter, compare the surname stored in the 'surname' variable with the surnames of all candidates who participated in the election.
    surname_filter = heroes_and_losers['NazwiskoImiona'].apply(lambda x: int(bool(regex.search(x)))) #Creating a filter (Data Series) by applying a regex expression to the 'NazwiskoImiona' column, where a result matching an actual candidate's surname is assigned a value of 1, and non-matching results are assigned a value of 0.
    general_filter = general_filter | surname_filter #Updating the overall filter to assign a value of 1 when any of the filters created during this iteration process matches a specific row, and a value of 0 when applying every single one of the created filters results in a 0 for that row.

candidates_with_famous_surnames = heroes_and_losers[general_filter & (heroes_and_losers['PozycjaNaLiscie'] != 1)]  #Excluding individuals who did receive a 1st place on the list, as they are considered the true leaders of their respective parties.

#1 While identifying top performers for each of the parties (whether they were individuals who finished significantly higher than their starting positions or had a high CandidatePower index), I noticed candidates with impressive scores, bearing the surnames: Hołownia, Trzaskowski, Kaczyński, Bosak, and Korwin-Mikke. At that moment, I made the decision to delve deeper into these candidates' profiles.
#2 Every candidate who shared a surname with one of the party leaders had a CandidatePower index higher than 2. This indicates that their performance was significantly better than the average percentage of votes received by other candidates from the same party who shared the same starting position. Bożenna Hołownia's CandidatePower index was 'only' 1, but as she was the only candidate starting from position 39, that value couldn't have been any different. However, she finished 35 positions higher, securing the 4th place, just one place away from getting a mandate in district 19 - Warsaw.
#3 There was only one exception identified here: Dominika Korwin-Mikke, who started from position 5 in Warsaw, gathered a CandidatePower index of 0.397, but she also finished in the 5th place. It appears that the dominant factor in this case was that the list in district 19 was entirely dominated by the party leader, Slawomir Mentzen, causing other candidates to gather a lower percentage of votes compared to the average candidate of that party who started from the same position. Another Korwin-Mikke, who started in district 1, had a CandidatePower index of 2.44. 
#4 Candidates who shared the same surname as political leaders generally belonged to the same political groups as the leaders with the same surname, except for one case. Jeremi Hołownia represented Nowa Lewica (not Trzecia Droga) and was placed 4th on the list. He secured 13.68% of Nowa Lewica's votes in district 1, performing significantly better than the average candidate in the 4th position for Nowa Lewica (5.12%).
#5 In the end, two candidates who shared their surname with political leaders secured parliamentary mandates. Karina Bosak, the wife of a group leader, triumphed over the former Konfederacja Leader Janusz Korwin-Mikke. Filip Kaczyński also secured a parliamentary mandate. This marks the third time he will serve as a member of parliament, but so far, he has remained a relatively lesser-known deputy.

#### QUICK GLANCE AT ELECTION GEOGRAPHICS #### 

only_parties_and_districts = candidates_copy.groupby(['OkregId', 'ListaId', 'NazwaKomitetu'])['Glosy'].sum().to_frame().reset_index() #Creating a new data frame object grouped by district ID ('OkregId') and party ('ListaId'). This change in aggregation level allows us to focus on analyzing each party in every district going forward. The 'candidates_copy' data frame was used, taking into consideration the votes of the parties that did not secure parliamentary seats.
votes_sum_district = only_parties_and_districts.groupby('OkregId')['Glosy'].sum().to_frame().reset_index() #Creating a data series with the sum of votes in each of the 41 districts. The length of the series is 41, and the merge will be performed with the inner parameter.
votes_sum_district.rename(columns = {'Glosy' : 'VotesSum'}, inplace = True)
only_parties_and_districts = only_parties_and_districts.merge(right = votes_sum_district, on = 'OkregId', how = 'inner')
only_parties_and_districts['Party_pct_district'] = round(100 * only_parties_and_districts['Glosy'] / only_parties_and_districts['VotesSum'],1) #The previous line of code added a new column with the sum of the votes in each district using the merge function. Now, the function calculates the percentage share of votes for each party in each of the districts.

all_parties_ids = list(only_parties_and_districts['ListaId'].unique()) #Creating a list with the IDs of all parties that participated in the election process.
elected_parties_ids = list(heroes_and_losers['ListaId'].unique()) #Creating a list of party IDs for parties that entered the parliament.

#1 The following line of code filters the data frame object to display only the parties that did not enter the parliament. These parties are then sorted by the percentage of votes they received in the district, from the highest to the lowest. The purpose of this task is to identify situations where a party did not enter parliament overall but still received more than 5% of the votes in a specific district. There is only one such example, where Mniejszość Niemiecka received 5.4% of the votes in district 21.
only_parties_and_districts[(only_parties_and_districts['ListaId'].isin(all_parties_ids)) & ~(only_parties_and_districts['ListaId'].isin(elected_parties_ids))].sort_values(by = 'Party_pct_district', ascending = False).head()

for party_id in elected_parties_ids: #This for loop analyzes each of the parties that entered parliament. The functions identify two districts where each party received its minimal and maximal support, measured as a percentage of all votes in the district, during the last elections. The loop then calculates the ratio between the highest level of support a party received and its lowest level of support. This ratio helps in understanding the variation in party support across different districts.
    max_geo_support = max(only_parties_and_districts['Party_pct_district'][only_parties_and_districts['ListaId'] == party_id])
    min_geo_support = min(only_parties_and_districts['Party_pct_district'][only_parties_and_districts['ListaId'] == party_id])
    max_to_min = max_geo_support / min_geo_support
    print(party_id, max_to_min, min_geo_support, max_geo_support)

#2 Konfederacja is the party with the smallest difference between the district where they received the maximum support (9.8%) and the district where they received the minimum support (5.6%). Consequently, the ratio between their maximum and minimum support is 1.75, which is the lowest among the analyzed parties.
#3 Trzecia Droga's ratio between the district with the maximal level of support and the district with the minimal level of support is slightly below 2 (1.93). The lowest support Trzecia Droga received was 9.8%, and the highest overall support they received was 18.9%.
#4 The ratio between the minimal and maximal support for KO and PiS is almost exactly the same: 2.79. The support range for KO is between 15.8% and 44.1%, while the range for PiS is between 19.6% and 54.7%.
#5 Nowa Lewica is a party with the largest difference in support levels across Poland. Their lowest support was 3.2% of votes in district 14, which is a region near Nowy Sącz, while their highest support was 21.6% of votes in district 32, which covers the Sosnowiec and Dąbrowa Górnicza region.
