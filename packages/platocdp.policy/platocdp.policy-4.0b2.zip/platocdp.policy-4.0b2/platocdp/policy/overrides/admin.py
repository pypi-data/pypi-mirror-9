from Products.CMFPlone.browser.admin import AddPloneSite 

class AddPlatoCDPSite(AddPloneSite):

    allowed_profiles = [
        'platocdp.policy:default',
    ]

    def filtered_extensions(self):
        profiles = self.profiles()
        extensions = [e for e in profiles['extensions'] if (
              e['id'] in self.allowed_profiles or 
              e['id'] in self.default_extension_profiles
        )]
        return extensions
