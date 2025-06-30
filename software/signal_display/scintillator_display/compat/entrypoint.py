from scintillator_display.compat.viewport_manager import ViewportManager

from scintillator_display.display.impl_controls.controls import Controls
from scintillator_display.display.orientation.app import App as IMPL_A
from scintillator_display.display.impl_b.window import Window as IMPL_B


def entrypoint():
    vm = ViewportManager()

    ratio = [1, 2, 2]

    impl_a = IMPL_A(init_mode='demo')
    impl_b = IMPL_B(init_mode='demo')
    impl_controls = Controls(impl_a, impl_b, vm)

    viewports = [impl_controls, impl_a, impl_b]
    for i, vp in enumerate(viewports):
        vp.viewport_shenanigans(vm, ratio[i])

    vm.generate_csv = False
    vm.end_csv = impl_a.data_manager.generate_data_csv
    
    vm.render_loop()
