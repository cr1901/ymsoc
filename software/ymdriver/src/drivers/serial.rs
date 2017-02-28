extern crate serial;
extern crate byteorder;

use api::{ArbDriver, ArbBank, ArbSettings};

use std::io;
use std::io::{Error, ErrorKind, SeekFrom};
use std::ffi::{OsStr, OsString};
use std::sync::Arc;
use std::sync::Mutex;

use self::byteorder::{ByteOrder, LittleEndian};

use self::serial::prelude::*;
use std::io::prelude::*;

/*
pub struct Settings {
    name : &AsRef<OsStr>,
    baud: serial::BaudRate
}
 */

// Avoid having to import extern serial into apps.
// Sigh... https://github.com/rust-lang/rust/issues/26264
// pub type BaudRate = serial::BaudRate;

pub struct Settings<'a, T: 'a + AsRef<OsStr> + ?Sized> {
    pub name : &'a T,
    pub baud: serial::BaudRate
}

// Implements SerialPort. Is there any way to abstract this so in lib.rs we don't have to commit
// to a specific serial port type until we're ready?
// i.e.
// impl<T> ArbDriver for T where T: SerialPort { in serial.rs
// and reference as trait object namespace in lib.rs.
//pub type SerialHandle = serial::SystemPort; // Does not work :(...

pub struct SerialHandle {
    port : Arc<Mutex<serial::SystemPort>>,
    bank: ArbBank,
    ptr: u16
}


impl ArbDriver for SerialHandle {
    fn acquire(bank : ArbBank, settings : ArbSettings) -> Box<ArbDriver> {

        let real_settings : Settings<OsStr> =
            match settings {
                ArbSettings::Serial(x) => x
            };

        let lock = Arc::new(Mutex::new(serial::open(&real_settings.name).unwrap()));

        {
            let mut port = lock.lock().unwrap();
            port.reconfigure(&|s| {
                try!(s.set_baud_rate(real_settings.baud));
                s.set_char_size(serial::Bits8);
                s.set_parity(serial::ParityNone);
                s.set_stop_bits(serial::Stop1);
                s.set_flow_control(serial::FlowNone);
                Ok(())
            });
        }

        Box::new(SerialHandle {
            port : lock,
            bank : bank,
            ptr : 0
        }) as Box<ArbDriver>
    }

    fn switch_bank(&self, bank: ArbBank) -> Box<ArbDriver> {
        Box::new(SerialHandle {
            port : self.port.clone(),
            bank : bank,
            ptr : 0
        }) as Box<ArbDriver>
    }
}

impl Write for SerialHandle  {
    fn write(&mut self, buf: &[u8]) -> io::Result<usize> {
        let iter = buf.chunks(4);

        for w in iter {
            if w.len() < 4 {
                let mut last_word : [u8; 4] = [0, 0, 0, 0];
                let valid = &mut last_word[0 .. w.len()];
                valid.copy_from_slice(w);
            }

            let mut ser_string : [u8; 7] = [0; 7];
            ser_string[0] = ((self.bank as u8) << 1) | 0x01;
            LittleEndian::write_u16(&mut ser_string[1 .. 3], self.ptr);
            {
                let dat = &mut ser_string[3 .. 7];
                dat.copy_from_slice(w);
                dat.reverse(); // Little endian through serial, but big-endian otherwise.
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
impl Seek for SerialHandle {
    fn seek(&mut self, pos: SeekFrom) -> io::Result<u64> {
        match pos {
            SeekFrom::Start(x) => {
                if x % 4 == 0 {
                    self.ptr = (x / 4) as u16;
                    Ok(x as u64)
                } else {
                    Err(Error::new(ErrorKind::InvalidInput, "Seek position must be multiple of 4!"))
                }
            },
            _ => Err(Error::new(ErrorKind::InvalidInput, "Only SeekFrom::Start supported!"))
        }
    }
}
