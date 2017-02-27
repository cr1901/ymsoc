extern crate ymdriver;
extern crate serial as extser;

use std::ffi::OsStr;

use ymdriver::drivers::serial;
use ymdriver::api as ymapi;


fn main() {
    let settings = ymapi::ArbSettings::Serial(serial::Settings::<OsStr> {
        name : OsStr::new("COM39"),
        baud : extser::Baud19200
    });

    let mut rom_drv = ymapi::DriverHandle::new(ymapi::ArbBank::ArbRom, settings);
    //let mut ctl_drv = ymapi::DriverHandle::new_handle(&rom_drv, ymapi::ArbBank::ArbCtl);
    let mut ctl_drv = ymapi::DriverHandle::new_handle(&*rom_drv, ymapi::ArbBank::ArbCtl);
    // let mut rom_drv = ArbDriver::<serial::SystemPort>::new_sys("COM39", 0, serial::Baud19200);
    // let mut ctl_drv = rom_drv.new_bank(3);
    //
    ctl_drv.write_word(0, 1);
    ctl_drv.write_word(0, 0);
}
