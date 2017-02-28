extern crate ymdriver;
extern crate argparse;
extern crate serial as extser;

use std::ffi::OsStr;
use std::fs::File;

use std::io::prelude::*;

use argparse::{ArgumentParser, StoreTrue, Store, StoreConst};

use ymdriver::drivers::serial;
use ymdriver::api as ymapi;

// FIXME: Make ArbSettings Clone work.
#[derive(Clone, Copy)]
enum DevOpts {
    Serial,
    Ethernet
}


fn main() {
    let mut verify = false;
    let mut baud = 19200;
    let mut dev_type = DevOpts::Serial;
    let mut device = String::new();
    let mut filename = String::new();
    let settings : ymapi::ArbSettings;

    {
        let mut ap = ArgumentParser::new();
        ap.set_description("Load firmware program onto a YMSoC design.");
        ap.refer(&mut verify)
            .add_option(&["-v", "--verify"], StoreTrue,
            "Verify after writing.");
        ap.refer(&mut baud)
            .add_option(&["-b", "--baud"], Store,
            "Baud rate if using serial port (ignored otherwise).");
        ap.refer(&mut dev_type)
            .add_option(&["-s", "--serial"], StoreConst(DevOpts::Serial),
            "Use serial port.")
            .add_option(&["-e", "--ethernet"], StoreConst(DevOpts::Ethernet),
            "Use ethernet port.")
            .required();
        ap.refer(&mut device)
            .add_argument("device", Store, "Device name to use.")
            .required();
        ap.refer(&mut filename)
            .add_argument("filename", Store, "Firmware file to write.")
            .required();
        ap.parse_args_or_exit();
    }

    settings = match dev_type {
        DevOpts::Serial => {
            ymapi::ArbSettings::Serial(serial::Settings::<OsStr> {
                name : OsStr::new(&device),
                baud : extser::BaudRate::from_speed(baud as usize)
            })
        },
        DevOpts::Ethernet => unimplemented!()
    };


    let mut rom_drv = ymapi::new(ymapi::ArbBank::ArbRom, settings);
    //let mut ctl_drv = ymapi::DriverHandle::new_handle(&rom_drv, ymapi::ArbBank::ArbCtl);
    let mut ctl_drv = ymapi::new_handle(&*rom_drv, ymapi::ArbBank::ArbCtl);

    let mut f = File::open(filename).unwrap();
    let mut buf = Vec::<u8>::new(); // Firmware is hundreds of kilos at most. Fully reading is safe.
    let firm_size = f.read_to_end(&mut buf).unwrap();

    ctl_drv.write_word(0, 1); // Hold CPU in reset
    rom_drv.write(&buf);
    ctl_drv.write_word(0, 0); // Reset done
}
