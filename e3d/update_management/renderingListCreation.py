# from SceneClass import Scene
from e3d.model_management.ModelInstanceClass import ModelInstance
from e3d.model_management.MaterialClass import Material
from collections import defaultdict


def getOrderedModelInstances(scene):
    """

    @return a list of model instances ordered by base model.
    @type scene: Scene
    """
    newList = []
    fullDic = defaultdict(list)

    for instance in scene._models.values():
        assert isinstance(instance, ModelInstance)
        fullDic[instance._baseModelID].append(instance)

    for key in fullDic.keys():
        fullDic[key] = orderByDiffuseTextureOrColor(fullDic[key])
        newList.extend(fullDic[key])

    return newList


def orderByDiffuseTextureOrColor(models):
    """

    @type models: list
    """
    newList = []
    fullDic = defaultdict(list)
    while models.__len__() > 0:
        model = models.pop(0)
        assert isinstance(model, ModelInstance)
        mat = model._materials[0]
        assert isinstance(mat, Material)
        if mat.useDiffuseTexture:
            fullDic[mat.diffuseTextureID].append(model)
        else:
            fullDic[str(mat._difCol)].append(model)

    for key in fullDic.keys():
        newList.extend(fullDic[key])

    return newList

