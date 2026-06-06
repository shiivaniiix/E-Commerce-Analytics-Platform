import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { profileService, addressService } from '../services';
import { getErrorMessage } from '../utils/helpers';
import Modal from '../components/common/Modal';
import LoadingSpinner from '../components/common/LoadingSpinner';

const EMPTY_ADDRESS = {
  address_line1: '',
  address_line2: '',
  city: '',
  state: '',
  country: '',
  pincode: '',
  is_default: false,
};

function Field({ label, children }) {
  return (
    <div>
      <div className="text-xs font-medium uppercase tracking-wide text-slate-400">{label}</div>
      <div className="mt-1 font-medium text-slate-900">{children}</div>
    </div>
  );
}

function TextInput({ label, ...props }) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        {...props}
        className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
      />
    </label>
  );
}

function ProfilePage() {
  const { user, updateUser, logout } = useAuth();
  const toast = useToast();

  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState(null);
  const [addresses, setAddresses] = useState([]);

  // Personal info edit state
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', phone_number: '' });
  const [savingProfile, setSavingProfile] = useState(false);

  // Address modal state
  const [addrModalOpen, setAddrModalOpen] = useState(false);
  const [addrForm, setAddrForm] = useState(EMPTY_ADDRESS);
  const [editingAddrId, setEditingAddrId] = useState(null);
  const [savingAddr, setSavingAddr] = useState(false);

  // Delete account confirm
  const [confirmDelete, setConfirmDelete] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [p, addrs] = await Promise.all([
        profileService.get(),
        addressService.getAll(),
      ]);
      setProfile(p);
      setForm({
        first_name: p.first_name || '',
        last_name: p.last_name || '',
        email: p.email || '',
        phone_number: p.phone_number || '',
      });
      setAddresses(addrs || []);
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const saveProfile = async () => {
    if (!form.first_name.trim() || !form.last_name.trim()) {
      toast.error('First and last name are required.');
      return;
    }
    setSavingProfile(true);
    try {
      const updated = await profileService.update({
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        email: form.email.trim(),
        phone_number: form.phone_number.trim() || null,
      });
      setProfile(updated);
      updateUser(updated);
      setEditing(false);
      toast.success('Profile updated');
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setSavingProfile(false);
    }
  };

  const deleteAccount = async () => {
    try {
      await profileService.remove();
      toast.success('Account deleted');
      logout();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  const openAddAddress = () => {
    setEditingAddrId(null);
    setAddrForm(EMPTY_ADDRESS);
    setAddrModalOpen(true);
  };

  const openEditAddress = (addr) => {
    setEditingAddrId(addr.address_id);
    setAddrForm({
      address_line1: addr.address_line1 || '',
      address_line2: addr.address_line2 || '',
      city: addr.city || '',
      state: addr.state || '',
      country: addr.country || '',
      pincode: addr.pincode || '',
      is_default: !!addr.is_default,
    });
    setAddrModalOpen(true);
  };

  const saveAddress = async () => {
    const required = ['address_line1', 'city', 'state', 'country', 'pincode'];
    if (required.some((k) => !String(addrForm[k]).trim())) {
      toast.error('Please fill in all required address fields.');
      return;
    }
    setSavingAddr(true);
    try {
      if (editingAddrId) {
        await addressService.update(editingAddrId, addrForm);
        toast.success('Address updated');
      } else {
        await addressService.create(addrForm);
        toast.success('Address added');
      }
      setAddrModalOpen(false);
      await loadData();
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setSavingAddr(false);
    }
  };

  const removeAddress = async (id) => {
    try {
      await addressService.remove(id);
      toast.success('Address removed');
      await loadData();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  const setDefault = async (id) => {
    try {
      await addressService.setDefault(id);
      toast.success('Default address updated');
      await loadData();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  if (loading) return <LoadingSpinner />;

  const displayName = profile ? `${profile.first_name} ${profile.last_name}` : (user ? `${user.first_name} ${user.last_name}` : '');

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
      <header className="mb-8 flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary text-2xl font-bold text-white shadow-lg shadow-primary/20">
          {(profile?.first_name || 'U').charAt(0).toUpperCase()}
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{displayName}</h1>
          <p className="text-sm text-slate-500">{profile?.email}</p>
        </div>
      </header>

      {/* Personal information */}
      <section className="mb-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Personal Information</h2>
          {!editing && (
            <button
              onClick={() => setEditing(true)}
              className="rounded-full border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              Edit
            </button>
          )}
        </div>

        {editing ? (
          <div className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <TextInput
                label="First Name"
                value={form.first_name}
                onChange={(e) => setForm({ ...form, first_name: e.target.value })}
              />
              <TextInput
                label="Last Name"
                value={form.last_name}
                onChange={(e) => setForm({ ...form, last_name: e.target.value })}
              />
              <TextInput
                label="Email"
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
              <TextInput
                label="Phone Number"
                value={form.phone_number}
                onChange={(e) => setForm({ ...form, phone_number: e.target.value })}
              />
            </div>
            <div className="flex gap-3 pt-2">
              <button
                onClick={saveProfile}
                disabled={savingProfile}
                className="rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-sky-600 disabled:opacity-50"
              >
                {savingProfile ? 'Saving…' : 'Save changes'}
              </button>
              <button
                onClick={() => {
                  setEditing(false);
                  setForm({
                    first_name: profile.first_name || '',
                    last_name: profile.last_name || '',
                    email: profile.email || '',
                    phone_number: profile.phone_number || '',
                  });
                }}
                className="rounded-full border border-slate-300 px-5 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div className="grid gap-5 sm:grid-cols-2">
            <Field label="First Name">{profile?.first_name || '—'}</Field>
            <Field label="Last Name">{profile?.last_name || '—'}</Field>
            <Field label="Email">{profile?.email || '—'}</Field>
            <Field label="Phone Number">{profile?.phone_number || '—'}</Field>
          </div>
        )}
      </section>

      {/* Address management */}
      <section className="mb-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Addresses</h2>
          <button
            onClick={openAddAddress}
            className="rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
          >
            + Add address
          </button>
        </div>

        {addresses.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-300 p-10 text-center">
            <p className="text-slate-500">You haven’t added any addresses yet.</p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {addresses.map((addr) => (
              <div
                key={addr.address_id}
                className={`relative rounded-2xl border p-5 ${
                  addr.is_default ? 'border-primary bg-primary/5' : 'border-slate-200'
                }`}
              >
                {addr.is_default && (
                  <span className="absolute right-4 top-4 rounded-full bg-primary px-2.5 py-0.5 text-xs font-semibold text-white">
                    Default
                  </span>
                )}
                <p className="font-medium text-slate-900">{addr.address_line1}</p>
                {addr.address_line2 && <p className="text-slate-600">{addr.address_line2}</p>}
                <p className="text-slate-600">
                  {addr.city}, {addr.state} {addr.pincode}
                </p>
                <p className="text-slate-600">{addr.country}</p>

                <div className="mt-4 flex flex-wrap gap-3 text-sm">
                  <button onClick={() => openEditAddress(addr)} className="font-medium text-primary hover:underline">
                    Edit
                  </button>
                  {!addr.is_default && (
                    <button onClick={() => setDefault(addr.address_id)} className="font-medium text-slate-600 hover:underline">
                      Set default
                    </button>
                  )}
                  <button onClick={() => removeAddress(addr.address_id)} className="font-medium text-red-600 hover:underline">
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Danger zone */}
      <section className="rounded-3xl border border-red-200 bg-red-50/50 p-6">
        <h2 className="text-lg font-semibold text-red-800">Danger zone</h2>
        <p className="mt-1 text-sm text-red-700">Deleting your account is permanent and removes all your data.</p>
        <button
          onClick={() => setConfirmDelete(true)}
          className="mt-4 rounded-full bg-red-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-red-500"
        >
          Delete account
        </button>
      </section>

      {/* Address modal */}
      <Modal
        title={editingAddrId ? 'Edit address' : 'Add address'}
        open={addrModalOpen}
        onClose={() => setAddrModalOpen(false)}
        footer={
          <div className="flex justify-end gap-3">
            <button
              onClick={() => setAddrModalOpen(false)}
              className="rounded-full border border-slate-300 px-5 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              onClick={saveAddress}
              disabled={savingAddr}
              className="rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-sky-600 disabled:opacity-50"
            >
              {savingAddr ? 'Saving…' : 'Save'}
            </button>
          </div>
        }
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <TextInput
              label="Address Line 1 *"
              value={addrForm.address_line1}
              onChange={(e) => setAddrForm({ ...addrForm, address_line1: e.target.value })}
            />
          </div>
          <div className="sm:col-span-2">
            <TextInput
              label="Address Line 2"
              value={addrForm.address_line2}
              onChange={(e) => setAddrForm({ ...addrForm, address_line2: e.target.value })}
            />
          </div>
          <TextInput label="City *" value={addrForm.city} onChange={(e) => setAddrForm({ ...addrForm, city: e.target.value })} />
          <TextInput label="State *" value={addrForm.state} onChange={(e) => setAddrForm({ ...addrForm, state: e.target.value })} />
          <TextInput label="Country *" value={addrForm.country} onChange={(e) => setAddrForm({ ...addrForm, country: e.target.value })} />
          <TextInput label="Pincode *" value={addrForm.pincode} onChange={(e) => setAddrForm({ ...addrForm, pincode: e.target.value })} />
          <label className="mt-2 flex items-center gap-2 sm:col-span-2">
            <input
              type="checkbox"
              checked={addrForm.is_default}
              onChange={(e) => setAddrForm({ ...addrForm, is_default: e.target.checked })}
              className="h-4 w-4 rounded border-slate-300 text-primary focus:ring-primary"
            />
            <span className="text-sm text-slate-700">Set as default address</span>
          </label>
        </div>
      </Modal>

      {/* Delete confirm modal */}
      <Modal
        title="Delete account?"
        open={confirmDelete}
        onClose={() => setConfirmDelete(false)}
        footer={
          <div className="flex justify-end gap-3">
            <button
              onClick={() => setConfirmDelete(false)}
              className="rounded-full border border-slate-300 px-5 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              onClick={deleteAccount}
              className="rounded-full bg-red-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-red-500"
            >
              Yes, delete my account
            </button>
          </div>
        }
      >
        <p className="text-slate-600">
          This action cannot be undone. All your data, including addresses and order history, will be permanently removed.
        </p>
      </Modal>
    </div>
  );
}

export default ProfilePage;
