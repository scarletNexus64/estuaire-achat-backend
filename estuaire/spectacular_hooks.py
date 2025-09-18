"""
Hooks personnalisés pour drf-spectacular
"""

def custom_preprocessing_hook(endpoints):
    """
    Hook de préprocessing pour ajouter automatiquement des tags basés sur l'application
    """
    filtered = []
    
    for path, path_regex, method, callback in endpoints:
        # Extraire le nom de l'application depuis le path
        path_parts = path.strip('/').split('/')
        if path_parts and path_parts[0]:
            app_name = path_parts[0].title()
            
            # Ajouter le tag de l'application
            if hasattr(callback, 'cls'):
                view_class = callback.cls
                if not hasattr(view_class, '_spectacular_annotation'):
                    view_class._spectacular_annotation = {}
                
                if 'tags' not in view_class._spectacular_annotation:
                    view_class._spectacular_annotation['tags'] = [app_name]
                elif app_name not in view_class._spectacular_annotation['tags']:
                    view_class._spectacular_annotation['tags'].append(app_name)
        
        filtered.append((path, path_regex, method, callback))
    
    return filtered