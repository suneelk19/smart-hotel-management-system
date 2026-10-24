# from django.db import models


# class Staff(models.Model):

#     DESIGNATION = (
#         ('Manager', 'Manager'),
#         ('Receptionist', 'Receptionist'),
#         ('Chef', 'Chef'),
#         ('Housekeeping', 'Housekeeping'),
#         ('Security', 'Security'),
#     )

#     name = models.CharField(max_length=100)

#     phone = models.CharField(max_length=15)

#     email = models.EmailField()

#     designation = models.CharField(
#         max_length=30,
#         choices=DESIGNATION
#     )

#     salary = models.DecimalField(
#         max_digits=10,
#         decimal_places=2
#     )

#     joining_date = models.DateField()

#     def __str__(self):
#         return self.name


from django.db import models


class Staff(models.Model):

    DESIGNATION = [

        ("Manager", "Manager"),
        ("Receptionist", "Receptionist"),
        ("Housekeeping", "Housekeeping"),
        ("Chef", "Chef"),
        ("Security", "Security"),
    ]

    name = models.CharField(max_length=100)

    designation = models.CharField(
        max_length=30,
        choices=DESIGNATION
    )

    phone = models.CharField(max_length=10)

    email = models.EmailField()

    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    joining_date = models.DateField()

    def __str__(self):
        return self.name