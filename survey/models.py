from django.db import models


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='companies/logos/', blank=True, null=True)
    invitation_code = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.invitation_code}"
    
    
# class Question(models.Model):
#     id = models.AutoField(primary_key=True)
#     text = models.TextField()
#     details = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.text
    
# class Answer(models.Model):
#     id = models.AutoField(primary_key=True)
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     text = models.TextField()