import dream7_credits_challenge1_data as data




first_model_type = data.credits1[data.team_mapping['orangeballs']][1]
first = data.credits1[data.team_mapping['orangeballs']][2].split()
first_model1 = [x for x,y in zip(first, first_model_type) if y==1]


second_model_type = data.credits1[data.team_mapping['orangeballs']][1]
second =  data.credits1[data.team_mapping['synmikro']][2].split()
second_model1 = [x for x,y in zip(second, second_model_type) if y==1]


third_model_type = data.credits1[data.team_mapping['bcb']][1]
third = data.credits1[data.team_mapping['bcb']][2].split()
third_model1 = [x for x,y in zip(third, third_model_type) if y==1]




