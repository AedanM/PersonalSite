import datetime

from django.db import models


class Education(models.Model):
    Institution: models.TextField = models.TextField()
    Qualification: models.TextField = models.TextField()
    Qualification_Level: models.TextField = models.TextField(blank=True, default="")
    Start_Year: models.IntegerField = models.IntegerField(default=2001)
    End_Year: models.IntegerField = models.IntegerField(default=datetime.date.today().year)

    def __str__(self) -> str:
        return self.Qualification + " from " + self.Institution


class Employment(models.Model):
    Employer: models.TextField = models.TextField()
    Job_Title: models.TextField = models.TextField()
    Skills_Gained: models.TextField = models.TextField(blank=True, default="")
    Responsibilities: models.TextField = models.TextField(blank=True, default="")
    Start_Year: models.IntegerField = models.IntegerField(default=2001)
    End_Year: models.IntegerField = models.IntegerField(default=datetime.date.today().year)

    def __str__(self) -> str:
        return self.Job_Title + " @ " + self.Employer
