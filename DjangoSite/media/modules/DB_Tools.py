from ..models import Media


def CleanDupes(model: Media):
    dupeCount = 0
    objList = model.objects.all()
    for obj in objList:
        matches = [x for x in objList if x.Title == obj.Title]
        if matches:
            firstInstance = matches[0]
            for m in matches:
                if m.id < firstInstance.id:  # type:ignore
                    firstInstance = m
            if obj != firstInstance:
                dupeCount += 1
                obj.delete()
    return f"{dupeCount} Duplicates Removed"
