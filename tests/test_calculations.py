from utils.calculations import calc_stat, stat_modifier


def test_calc_stat_hp():
    quaxly_hp = calc_stat(50, 55, 252, 31, True)

    assert quaxly_hp == 162, "HP calc is wrong"


def test_calc_stat_atk():
    quaxly_atk = calc_stat(50, 65, 252, 31, False)

    assert quaxly_atk == 117, "Atk calc is wrong"


def test_stat_modifier_pos():

    #  gholdengo stat checks
    ghol_test_1 = stat_modifier(num_stages=2, stat=calc_stat(50, 84, 252, 31))
    assert ghol_test_1 == 272, "Ghol test is wrong"


def test_stat_modifier_neg():

    ghol_test_2 = stat_modifier(num_stages=-3, stat=calc_stat(50, 84, 252, 31))
    assert ghol_test_2 == 54, "Ghol test is wrong"


# print(speed_check("gholdengho", "gholdengo", 2, -1, 252, 252))
# print(speed_check("gholdengho", "gholdengo", 2, 2, 252, 252))
# print(speed_check("gholdengho", "gholdengo", 2, 2, 252, 200))
# print(speed_check("flutter man", "iron bundle"))
# print(speed_check("flutter man", "iron bundle", p1_stat_changes=1))
