//! C-compatible MuseAir BFast 64-bit hash, loaded by SpeeduPy through ctypes.
//!
//! The function is the one https://github.com/JoaoLopez/museair (commit
//! 91e7304) added to the MuseAir crate, moved here unchanged except for the
//! path of the call: `museair::bfast::hash` instead of `crate::bfast::hash`.

/// C-compatible wrapper for MuseAir BFast 64-bit hash.
///
/// # Safety
/// - `data` must point to a valid buffer of length `len`
/// - `out` must be a valid pointer to a u64
#[no_mangle]
pub extern "C" fn museair_bfast_64(data: *const u8, len: usize, seed: u64, out: *mut u64) {
    let slice = unsafe { std::slice::from_raw_parts(data, len) };

    let hash = museair::bfast::hash(slice, seed);

    unsafe {
        *out = hash;
    }
}
