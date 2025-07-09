from software.signal_display.scintillator_display.display.impl_a.data_manager import test
from software.signal_display.scintillator_display.display.impl_b.input_data import DataReception

def test_instantiate():
    impl_a = test(debug=True)
    impl_b = DataReception(debug=True)

    assert not impl_a.has_data()
    assert impl_b.has_new_data()
    assert impl_b.get_data_from_arduino()
    assert not impl_b.has_new_data()

def test_interpet_raw_data():
    impl_a = test(debug=True)
    impl_b = DataReception(debug=True)

    a = 0b01010101010101010101010101010101
    A = [
        [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)],
        [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)],
    ]
    
    A_a = impl_a.interpret_raw_data(a)
    assert A == A_a

    A_b = impl_b.string_int32_to_scintillator_binary(a)
    assert A == A_b


    b = 0b10101010101010101010101010101010
    B = [
        [(1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0)],
        [(1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0)],
    ]

    B_a = impl_a.interpret_raw_data(b)
    assert B == B_a

    B_b = impl_b.string_int32_to_scintillator_binary(b)
    assert B == B_b


if __name__ == "__main__":
    test_interpet_raw_data()
