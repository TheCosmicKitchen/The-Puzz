-- Guests no longer write anything: their progress stays on the device. Only signed-in users
-- (Supabase Auth, role `authenticated`) may insert. Applied together with the Muze half as `no_guest_writes`.
revoke insert on public.puzz_events from anon;
drop policy puzz_events_insert on public.puzz_events;
create policy puzz_events_insert on public.puzz_events
  for insert to authenticated
  with check (day between current_date - 1 and current_date + 1);
