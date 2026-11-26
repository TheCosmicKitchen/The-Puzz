-- The Puzz: anonymous daily stats.
-- Each page sends one 'play' row when today's daily opens and one 'solve' row when it's finished.
-- No accounts and no device id: a row is just game, day, time, the player's streak and a little
-- free-form `meta` (moves, peeks, difficulty...) for whatever a game wants to count later.
-- Browsers may only INSERT. Everything they read comes from puzz_stats(), which returns totals only.

create table public.puzz_events (
  id         bigint generated always as identity primary key,
  game       text not null check (game in ('hex', 'sb', 'jg', 'ws', 'ds', 'ts', 'st', 'ta', 'nw')),
  day        date not null,
  kind       text not null check (kind in ('play', 'solve')),
  seconds    integer check (seconds between 0 and 86400),
  streak     integer check (streak between 0 and 10000),
  meta       jsonb not null default '{}'::jsonb
             check (jsonb_typeof(meta) = 'object' and pg_column_size(meta) <= 2048),
  created_at timestamptz not null default now()
);
create index puzz_events_day_game on public.puzz_events (day, game);

alter table public.puzz_events enable row level security;
revoke all on public.puzz_events from anon, authenticated;
grant insert on public.puzz_events to anon, authenticated;

-- Insert only, for today's puzzle give or take a timezone. No select, update or delete policy exists,
-- so those are refused for every browser.
create policy puzz_events_insert on public.puzz_events
  for insert to anon, authenticated
  with check (day between current_date - 1 and current_date + 1);

-- Totals for one day, plus all-time solves. `meta` gives the median of every numeric key per game,
-- so a game that starts sending {"moves": 12} gets a moves median here with no schema change.
create function public.puzz_stats(p_day date default current_date)
returns jsonb
language sql stable security definer set search_path = ''
as $$
  with today as (select * from public.puzz_events where day = p_day),
  games as (
    select game, jsonb_build_object(
      'plays', count(*) filter (where kind = 'play'),
      'solved', count(*) filter (where kind = 'solve'),
      'median_seconds', percentile_disc(0.5) within group (order by seconds) filter (where kind = 'solve'),
      'best_seconds', min(seconds) filter (where kind = 'solve'),
      'longest_streak', max(streak) filter (where kind = 'solve')) as g
    from today group by game
  ),
  meta as (
    select game, jsonb_object_agg(key, med) as m from (
      select t.game, e.key, percentile_disc(0.5) within group (order by (e.value #>> '{}')::numeric) as med
      from today t, jsonb_each(t.meta) e
      where t.kind = 'solve' and jsonb_typeof(e.value) = 'number'
      group by t.game, e.key) k
    group by game
  )
  select jsonb_build_object(
    'day', p_day,
    'solved_today', (select count(*) from today where kind = 'solve'),
    'solved_all_time', (select count(*) from public.puzz_events where kind = 'solve'),
    'longest_streak_today', (select max(streak) from today where kind = 'solve'),
    'games', coalesce((select jsonb_object_agg(g.game, g.g || jsonb_build_object('meta', coalesce(m.m, '{}'::jsonb)))
                       from games g left join meta m using (game)), '{}'::jsonb));
$$;
revoke execute on function public.puzz_stats(date) from public;
grant execute on function public.puzz_stats(date) to anon, authenticated;
