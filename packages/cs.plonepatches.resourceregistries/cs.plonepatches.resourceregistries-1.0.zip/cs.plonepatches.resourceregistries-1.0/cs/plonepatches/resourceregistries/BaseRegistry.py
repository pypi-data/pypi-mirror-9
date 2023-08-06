
def cookResources(self):
    """Cook the stored resources. Patched version:
       find the most compatible concatenated resource and
       concatenate a resource in there.
    """
    if self.ZCacheable_isCachingEnabled():
        self.ZCacheable_invalidate()

    self.concatenatedResourcesByTheme = {}
    self.cookedResourcesByTheme = {}

    bundlesForThemes = self.getBundlesForThemes()
    for theme, bundles in bundlesForThemes.items():

        resources = [r.copy() for r in self.getResources() if r.getEnabled()]
        results = []

        concatenatedResources = self.concatenatedResourcesByTheme[theme] = {}

        for resource in resources:

            # Skip resources in bundles not in this theme. None bundles
            # are assumed to

            bundle = resource.getBundle()
            if bundle not in bundles:
                continue

            if results:
                stored = False
                for previtem in reversed(results):
                    # Is this resource compatible the previous one we used?
                    if resource.getCookable() and previtem.getCookable() \
                           and self.compareResources(resource, previtem):
                        res_id = resource.getId()
                        prev_id = previtem.getId()
                        self.finalizeResourceMerging(resource, previtem)

                        # Add the original id under concatenated resources or
                        # create a new one starting with the previous item
                        if concatenatedResources.has_key(prev_id):
                            concatenatedResources[prev_id].append(res_id)
                        else:
                            magic_id = self.generateId(resource, previtem)
                            concatenatedResources[magic_id] = [prev_id, res_id]
                            previtem._setId(magic_id)

                        stored = True
                        break

                if not stored:
                    if resource.getCookable() or resource.getCacheable():
                        magic_id = self.generateId(resource)
                        concatenatedResources[magic_id] = [resource.getId()]
                        resource._setId(magic_id)
                    results.append(resource)

            else:  # No resources collated yet

                # If cookable or cacheable, generate a magic id, change
                # the resource id to be this id, and record the old id in the
                # list of ids for this magic id under concatenated resources
                if resource.getCookable() or resource.getCacheable():
                    magic_id = self.generateId(resource)
                    concatenatedResources[magic_id] = [resource.getId()]
                    resource._setId(magic_id)
                results.append(resource)
            # import pdb; pdb.set_trace()
            # a = 1

        # Get the raw list of resources and store these as well in
        # concatenated resources
        resources = self.getResources()
        for resource in resources:
            concatenatedResources[resource.getId()] = [resource.getId()]

        # self.cookedResourcesByTheme[theme] = tuple(anonymousResources +
        #     memberResources + otherResources)
        self.cookedResourcesByTheme[theme] = tuple(results)
