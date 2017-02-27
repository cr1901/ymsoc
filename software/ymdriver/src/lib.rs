extern crate byteorder;

pub mod drivers;

pub mod api {
    use std::ffi::OsStr;
    use std::io::SeekFrom;

    use byteorder::{ByteOrder, LittleEndian};

    use std::io::prelude::*;
    use drivers::*;

    pub struct DriverHandle {
        // Look into abstract return types?
        //port: Box<ArbDriver>
    }

    pub enum ArbSettings<'a> {
        Serial(serial::Settings<'a, OsStr>)
    }

    #[derive(Clone, Copy)]
    pub enum ArbBank {
        ArbRom = 0,
        ArbDta = 2,
        ArbCtl = 3
    }

    // Drivers implement this trait, and they should be okay for use everywhere.
    pub trait ArbDriver : Write + Seek {
        // Get our generic driver. Self: Sized disables dynamic dispatch for the fcn in question.
        fn acquire(bank : ArbBank, settings : ArbSettings) -> Box<ArbDriver> where Self: Sized;
        fn switch_bank(&self, bank: ArbBank) -> Box<ArbDriver>;
        fn write_word(&mut self, addr: u16, data: u32) -> () {
            self.seek(SeekFrom::Start(addr as u64));
            let mut data_word : [u8; 4] = [0; 4];
            LittleEndian::write_u32(&mut data_word, data);
            self.write(&data_word);
        }
    }


    impl DriverHandle {
        pub fn new(bank : ArbBank, settings : ArbSettings) -> Box<ArbDriver> {

            match settings {
                //Serial doesn't work... why?
                ArbSettings::Serial(x) => {
                    serial::SerialHandle::acquire(bank, ArbSettings::Serial(x)) as Box<ArbDriver>
                }
            }
        }

        //pub fn new_handle<T : ArbDriver + ?Sized> (drv: &T, bank: ArbBank) -> Box<ArbDriver> {
        pub fn new_handle(drv: &ArbDriver, bank: ArbBank) -> Box<ArbDriver> {
            drv.switch_bank(bank)
        }
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
    }
}
