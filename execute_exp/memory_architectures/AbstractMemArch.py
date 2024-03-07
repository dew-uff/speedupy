class AbstractMemArch():
    def get_initial_cache_entries(self): pass #OLD populate_cache_dictionary
    def get_cache_entry(self, func_call_hash:str, *args): pass #OLD get_cache_data
    def create_cache_entry(self, func_call_hash:str, func_return, *args): pass #OLD add_to_cache
    def save_new_cache_entries(self): pass #OLD save_new_cache_data