extern crate serial;
extern crate byteorder;

use std::io;
use std::io::{Error, ErrorKind, SeekFrom};
use std::ffi::OsStr;
use std::sync::Arc;
use std::sync::Mutex;

use std::io::prelude::*;
use serial::prelude::*;

use byteorder::{ByteOrder, LittleEndian};


struct ArbDriver<T: SerialPort> {
    port: Arc<Mutex<T>>,
    bank: u8,
    ptr: u16
}

impl<T: SerialPort> ArbDriver<T> {
    fn new_sys<S: AsRef<OsStr> + ?Sized>(name: &S, bank: u8, baud: serial::BaudRate) -> ArbDriver<serial::SystemPort> {
        let lock = Arc::new(Mutex::new(serial::open(name).unwrap()));

        {
            let mut port = lock.lock().unwrap();

            port.reconfigure(&|settings| {
                try!(settings.set_baud_rate(baud));
                settings.set_char_size(serial::Bits8);
                settings.set_parity(serial::ParityNone);
                settings.set_stop_bits(serial::Stop1);
                settings.set_flow_control(serial::FlowNone);
                Ok(())
            });
        }

        ArbDriver::<serial::SystemPort> {
            port: lock,
            bank: bank,
            ptr: 0
        }
    }

    // Resets seek position to 0.
    fn new_bank(&self, bank: u8) -> ArbDriver<T> {
        ArbDriver::<T> {
            port: self.port.clone(),
            bank: bank,
            ptr: 0
        }
    }

    fn write_word(&mut self, addr: u16, data: u32) -> () {
        self.seek(SeekFrom::Start(addr as u64));
        let mut data_word : [u8; 4] = [0; 4];
        LittleEndian::write_u32(&mut data_word, data);
        self.write(&data_word);
    }
}


impl<T: SerialPort> Write for ArbDriver<T> {
    fn write(&mut self, buf: &[u8]) -> io::Result<usize> {
        let iter = buf.chunks(4);

        for w in iter {
            if w.len() < 4 {
                let mut last_word : [u8; 4] = [0, 0, 0, 0];
                let valid = &mut last_word[0 .. w.len()];
                valid.copy_from_slice(w);
            }

            let mut ser_string : [u8; 7] = [0; 7];

            ser_string[0] = (self.bank << 1) | 0x01;
            LittleEndian::write_u16(&mut ser_string[1 .. 3], self.ptr);
            {
                let dat = &mut ser_string[3 .. 7];
                dat.copy_from_slice(w);
            }

            let mut port = self.port.lock().unwrap();
            port.write(&ser_string);
            self.ptr += 1;
        }

        Ok(buf.len())
    }

    fn flush(&mut self) -> io::Result<()> {
        Ok(())
    }
}


// Why serial::SerialDevice bound, not SerialPort?
// impl<T> Seek for ArbDriver<T> {
// Actually SerialDevice doesn't work either b/c trait bounds.
// impl<T> Seek for ArbDriver<T> where T: serial::SerialDevice {
impl<T: SerialPort> Seek for ArbDriver<T> {
    fn seek(&mut self, pos: SeekFrom) -> io::Result<u64> {
        match pos {
            SeekFrom::Start(x) => {
                self.ptr = x as u16;
                Ok(x as u64)
            },
            _ => Err(Error::new(ErrorKind::InvalidInput, "Only SeekFrom::Start supported!"))
        }
    }
}



fn main() {
    let mut rom_drv = ArbDriver::<serial::SystemPort>::new_sys("COM39", 0, serial::Baud19200);
    let mut ctl_drv = rom_drv.new_bank(3);

    ctl_drv.write_word(0, 1);
    ctl_drv.write_word(0, 0);
}
