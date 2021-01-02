rules = {"X24B2": {"name": "timer_1", "trigger": {"time": {"start": "18:30", "end": "18:45"}},
                       "action": {"do": "ON", "block": False, "time": 60}}}

for ident, rule in rules.items():
    print(ident)
    print(str(rule))