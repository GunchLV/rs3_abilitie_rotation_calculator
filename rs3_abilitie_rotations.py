import pandas as pd


'''

▓▓ - abilitie is used
▓░░░ - abilitie is used continuesly - channeled abities
CD - abilitie is on cooldown
. - abilitie is ready to be used

cooldown is measured in ticks
'''

# create table formating for each abilitie
icon_map = {}
for ab in ['Assault','Dismember','Slice','Slaughter','Sever']:
    ab_style = f'<div style="text-align:center">\n<img src="icons/{ab.lower()}.png" width="32"><br><span>{ab}</span></div>'
    icon_map.update({ab: ab_style})


abilitie_dmg = 1920
dmg_boosts = 18 # extra boost in %

# Define abilities with type 
#   dot is dmg over time --> bleed
#   dmg is in %, it will be multiplied with abilitie dmg later
abilities = {
    # basic
    'Sever': {'cd': 9,  'mechanic': 'instant', 'damage': 120, 'adrenaline': +8, 'type':'basic', 'hits':1},
    'Slice': {'cd': 5,  'mechanic': 'instant', 'damage': 105, 'adrenaline': +8, 'type':'basic', 'hits':1},
    'Dismember': {'cd': 25,  'mechanic': 'dot', 'damage': 115, 'adrenaline': +8, 'type':'basic', 'hits':5},
    
    # treshold
    'Assault': {'cd': 50, 'mechanic': 'channel', 'damage': 560, 'adrenaline': -15, 'type':'treshold', 'hits':4},    
    'Slaughter': {'cd': 50, 'mechanic': 'dot', 'damage': 175, 'adrenaline': -15, 'type':'treshold', 'hits':5},
    
     # ultimate
    'Overpower': {'cd': 50,  'mechanic': 'instant', 'damage': 600, 'adrenaline': -100, 'type':'ultimate', 'hits':1},
}

# Planned rotation
rotation = ['Assault','Slaughter','Dismember','Sever','Slice','Slice']
abilities = {k: v for k, v in abilities.items() if k in rotation} # filter out those that are not used so they dont show in result table

ticks = 25 # How long time period will be simulated
timeline = []
cooldowns = {a: 0 for a in abilities}
channels = {a: 0 for a in abilities}
adrenaline = 100 # starting adrenaline
adrenaline_upper_limit = 100
total_damage = 0
rot_index = 0

starting_adrenaline = adrenaline # for print statment at output
pending_bleed_dmg=[] # list to store all pending bleed for future ticks
channeled_statuss_visuals = ['▓░░░','▓▓░░','▓▓░░','▓▓▓░','▓▓▓░','▓▓▓▓','▓▓▓▓']
for t in range(ticks):
    row = {'Tick':t+1, 'Time(s)':round(t*0.6,1), 'Adrenaline':adrenaline, 'Damage':0, 'Total damage':0}
    
    # status marks
    for a in abilities:
        if channels[a] > 0:
            row[a] = channeled_statuss_visuals[-channels[a]] # abilitie is channeled on continue to work
        elif cooldowns[a] > 0:
            row[a] = 'CD' # cooldown
        else:
            row[a] = '.' # ready to use    
    
    # Use next ability from rotation if free
    if rot_index < len(rotation):
        abil = rotation[rot_index]
        # Can use if not channeling anything
        if all(v == 0 for v in channels.values()):
            if cooldowns[abil] == 0:
                data = abilities[abil]
                if data['mechanic'] == 'channel':
                    channels[abil] = data['hits'] * 2 # because 1 hit every 2 ticks (1.2s)
                    cooldowns[abil] = data['cd']
                    row[abil] = '▓░░░'
                    row['Damage'] += (data['damage'] / 100 * abilitie_dmg) * (1+dmg_boosts/100) / data['hits']
                    adrenaline += data['adrenaline']
                    adrenaline = adrenaline if adrenaline <= adrenaline_upper_limit else adrenaline_upper_limit
                    total_damage += row['Damage']
                    
                    new_stored_dmg=[]
                    for i in range(0, data['hits']-1):
                        new_stored_dmg.append(0)
                        new_stored_dmg.append(row['Damage'])
                    new_stored_dmg[0] = 0
                    new_stored_dmg.insert(0,0)
                    
                    currenty_pending_bleed = pending_bleed_dmg
                    pending_bleed_dmg = []
                    length = max(len(new_stored_dmg), len(currenty_pending_bleed))
                    for i in range(length):
                        pending_bleed_dmg.append((currenty_pending_bleed[i] if i < len(currenty_pending_bleed) else 0) +
                                                 (new_stored_dmg[i] if i < len(new_stored_dmg) else 0))                    
                    rot_index += 1
                
                elif data['mechanic'] == 'instant':
                    cooldowns[abil] = data['cd']
                    row[abil] = '▓▓'
                    row['Damage'] += (data['damage'] / 100 * abilitie_dmg) * (1+dmg_boosts/100)
                    adrenaline += data['adrenaline']
                    adrenaline = adrenaline if adrenaline <= adrenaline_upper_limit else adrenaline_upper_limit
                    total_damage += row['Damage']
                    rot_index += 1
                
                elif data['mechanic'] == 'dot':
                    cooldowns[abil] = data['cd']
                    row[abil] = '▓▓'
                    row['Damage'] += (data['damage'] / 100 * abilitie_dmg) * (1+dmg_boosts/100) / data['hits']
                    adrenaline += data['adrenaline']
                    adrenaline = adrenaline if adrenaline <= adrenaline_upper_limit else adrenaline_upper_limit
                    total_damage += row['Damage']
                    new_bleed_dmg=[]
                    for i in range(0, data['hits']-1):
                        new_bleed_dmg.append(0)
                        new_bleed_dmg.append(row['Damage'])
                    new_bleed_dmg[0] = 0
                    new_bleed_dmg.insert(0,0)
                    
                    currenty_pending_bleed = pending_bleed_dmg
                    pending_bleed_dmg = []
                    length = max(len(new_bleed_dmg), len(currenty_pending_bleed))
                    for i in range(length):
                        pending_bleed_dmg.append((currenty_pending_bleed[i] if i < len(currenty_pending_bleed) else 0) +
                                                 (new_bleed_dmg[i] if i < len(new_bleed_dmg) else 0))                        
                    rot_index += 1
        
    if len(pending_bleed_dmg)>0: # use pending bleed dmg from previous attacks
        row['Damage'] += pending_bleed_dmg[0]
        total_damage += pending_bleed_dmg[0]
        pending_bleed_dmg.pop(0)
            
    # Decrement counters
    for a in abilities:
        if channels[a] > 0:
            channels[a] -= 1
        if cooldowns[a] > 0:
            cooldowns[a] -= 1
    
    row['Adrenaline'] = adrenaline
    row['Total damage'] = total_damage
    timeline.append(row)

df = pd.DataFrame(timeline)
df_renamed = df.rename(columns=icon_map)
result_table = (df_renamed.style.hide(axis="index")
                 .set_table_attributes('style="display:block; max-height:700px; overflow:auto;"')
                 .format(precision=1).set_table_styles([
                     {'selector': 'thead th',
                      'props': [('background-color', '#1F1F1F'), ('position', 'sticky'), ('top', '0'), ('z-index', '2')]}])
                 .set_properties(**{'text-align': 'center'}))

print(f'\nStarting adrenaline: {starting_adrenaline}% / Damage boosts: +{dmg_boosts}%')
print(f'''Current rotation --> {str(rotation).replace("'",'')[1:-1]}''')
print(f'Total time: {ticks} ticks / Total Damage: {int(total_damage)} / DPS: {round(total_damage/(ticks*0.6),1)} / DPM: {round(total_damage/(ticks*0.6),1)*60}')

# Allow HTML rendering
from IPython.display import display, HTML
display(HTML(result_table.to_html(escape=False)))