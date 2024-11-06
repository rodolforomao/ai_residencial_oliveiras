# utils/management_request_status_util.py
import json

class ManagementRequestsSatus:
    
    def __init__(self, schedule = None):
        self.schedule_sent_status = schedule

    def has_sent_successfully(self, json_data):
        json_str = json.dumps(json_data, sort_keys=True)
        for entry in self.schedule_sent_status:
            if entry['json_data'] == json_str:
                status_code_output = entry.get('status_code_output') == 200
                status_code_schedule = entry.get('status_code_schedule') == 'confirmed'
                return status_code_output, status_code_schedule
        return False, False
    
    def add_update_or_status_code(self, json_data, status_code_output = None, status_code_schedule = None):
        json_str = json.dumps(json_data, sort_keys=True)
        
        if self.schedule_sent_status:
            for entry in self.schedule_sent_status:
                if entry['json_data'] == json_str:
                    if status_code_output is not None:
                        entry['status_code_output'] = status_code_output
                        print(f"Status code atualizado: Output: {status_code_output} para o json_data.")
                    if status_code_schedule is not None:
                        entry['status_code_schedule'] = status_code_schedule
                        print(f"Status code atualizado: Schedule: {status_code_schedule} para o json_data.")
                    
                    return True
        self.schedule_sent_status.append({
            'json_data': json.dumps(json_data, sort_keys=True),
            'status_code_output': status_code_output,
            'status_code_schedule': status_code_schedule
        })
        print(f"Novo json_data adicionado com status_code_output {status_code_output} e status_code_schedule {status_code_schedule}.")
        return True