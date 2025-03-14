import os

class TemplateParser:
    """
    A utility class for parsing localized templates based on the user's language preference.

    This class is used to retrieve and substitute variables in localized templates
    stored in language-specific directories under a "locales" folder.
    """

    def __init__(self, language: str=None, default_language='en'):
        """
        Initialize a TemplateParser instance.

        Args:
            language (str, optional): The preferred language code (e.g., 'en', 'fr'). 
                                      If not provided, defaults to the default_language.
            default_language (str): The fallback language code. Defaults to 'en'.
            language (str): The currently active language code.
        """
        self.current_path = os.path.dirname(os.path.abspath(__file__)) # to get the parent forlder name "templates"
        self.default_language = default_language 
        self.language = None

        self.set_language(language)

    
    def set_language(self, language: str):
        """ Set the active language for the template parser."""
        if not language:
        # If the specified language does not exist in the "locales" directory, it falls back
        # to the default language.
            self.language = self.default_language

        # get the path of defined languages
        language_path = os.path.join(self.current_path, "locales", language)
        if os.path.exists(language_path):
            self.language = language
        else:
            self.language = self.default_language

    def get(self, group: str, key: str, vars: dict={}):
        """
        Retrieve a localized template value and substitute variables into it.

        Args:
            group (str): The name of the group (module) to load (e.g., "rag").
            key (str): The key/variable to retrieve from the module (e.g., "document_prompt").
            vars (dict, optional): A dictionary of variables to substitute into the template.
                                   Defaults to an empty dictionary.

        Returns:
            str or None: The localized and formatted template string if found, or `None` if
                         the group or key does not exist.
        """
        if not group or not key:
            return None
        
        # look up for a Python file in the "locales" directory corresponding to the specified group (rag) and language. 
        group_path = os.path.join(self.current_path, "locales", self.language, f"{group}.py" )
        targeted_language = self.language

        # If the file is not found in the specified language, it looks up for it in the default language. 
        if not os.path.exists(group_path):
            group_path = os.path.join(self.current_path, "locales", self.default_language, f"{group}.py" )
            targeted_language = self.default_language

        if not os.path.exists(group_path):
            return None
        
        # import group (rag) module (file) -- it's like doing import statment
        module = __import__(f"stores.llm.templates.locales.{targeted_language}.{group}", fromlist=[group])

        if not module:
            return None
        
        # get variables names
        key_attribute = getattr(module, key)
        # put needed values
        return key_attribute.substitute(vars)
