from scintillator_display.compat.viewport_manager import ViewportManager

from scintillator_display.display.impl_controls.controls import Controls
#from scintillator_display.display.impl_a.app import App as IMPL_A
from scintillator_display.display.orientation.app import App as IMPL_A
from scintillator_display.display.impl_b.window import Window as IMPL_B


def entrypoint():
    vm = ViewportManager()

    '''
    x_ratio format = (start, end, total)
    y_ratio format = (start, end, total)
    '''
    impl_a = IMPL_A(init_mode='demo',            x_ratio=(1, 3, 5), y_ratio=(0, 1, 1))
    impl_b = IMPL_B(init_mode='demo',            x_ratio=(3, 5, 5), y_ratio=(0, 1, 1))
    impl_controls = Controls(impl_a, impl_b, vm, x_ratio=(0, 1, 5), y_ratio=(0, 1, 1))

    viewports = [impl_controls, impl_a, impl_b]
    for vp in viewports:
        vp.viewport_shenanigans(vm)

    vm.generate_csv = False
    vm.end_csv = impl_a.data_manager.generate_data_csv
    
    vm.render_loop()
