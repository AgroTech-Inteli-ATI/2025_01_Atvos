require('dotenv').config();
const { Client } = require('pg');

const sql = `
-- Tabelas
create table if not exists public.travel (
  id                bigserial primary key,
  asset_description text        not null,
  register_number   text        not null,
  asset_id          bigint      not null,
  garage_name       text,
  full_distance     numeric(10,2) not null check (full_distance >= 0),
  datetime          timestamptz not null
);

create table if not exists public.stop (
  id                  bigserial primary key,
  departure_datetime  timestamptz not null,
  driver              text,
  departure_site      text,
  trip_time           interval     not null,
  trip_distance       numeric(10,2) not null check (trip_distance >= 0),
  arrival_datetime    timestamptz  not null,
  arrival_site        text,
  travel_id           bigint       not null references public.travel(id) on delete cascade
);

create index if not exists idx_stop_travel_id on public.stop(travel_id);
create index if not exists idx_stop_departure_datetime on public.stop(departure_datetime);
create index if not exists idx_stop_arrival_datetime on public.stop(arrival_datetime);

create table if not exists public.bill (
  id          bigserial primary key,
  fix_cost    numeric(14,2) not null check (fix_cost >= 0),
  variable_km numeric(10,2) not null check (variable_km >= 0),
  travel_id   bigint        not null references public.travel(id) on delete cascade,
  datetime    timestamptz   not null
);

create index if not exists idx_bill_travel_id on public.bill(travel_id);
create index if not exists idx_bill_datetime on public.bill(datetime);

create table if not exists public.raw_layer (
  id         bigserial primary key,
  url        text        not null unique,
  travel_id  bigint      not null references public.travel(id) on delete cascade,
  datetime   timestamptz not null
);

create index if not exists idx_raw_layer_travel_id on public.raw_layer(travel_id);
create index if not exists idx_raw_layer_datetime on public.raw_layer(datetime);

create table if not exists public.staging_layer (
  id           bigserial primary key,
  url          text        not null unique,
  raw_layer_id bigint      not null references public.raw_layer(id) on delete cascade,
  datetime     timestamptz not null
);

create index if not exists idx_staging_layer_raw_id on public.staging_layer(raw_layer_id);
create index if not exists idx_staging_layer_datetime on public.staging_layer(datetime);

-- Novas entidades para suportar funcionalidades do wireframe

-- Unidade operacional
create table if not exists public.unit (
  id          bigserial primary key,
  name        varchar(50) not null unique,
  description varchar(255)
);

-- Categoria de ocorrência
create table if not exists public.occurrence_category (
  id   bigserial primary key,
  name varchar(100) not null unique
);

-- Ocorrências vinculadas a viagens
create table if not exists public.occurrence (
  id           bigserial primary key,
  travel_id    bigint       not null references public.travel(id) on delete cascade,
  unit_id      bigint       references public.unit(id) on delete set null,
  carrier_name varchar(255),
  category_id  bigint       references public.occurrence_category(id) on delete set null,
  root_cause   text,
  description  text,
  datetime     timestamptz  not null
);

create index if not exists idx_occurrence_travel_id on public.occurrence(travel_id);
create index if not exists idx_occurrence_unit_id on public.occurrence(unit_id);
create index if not exists idx_occurrence_category_id on public.occurrence(category_id);
create index if not exists idx_occurrence_datetime on public.occurrence(datetime);

-- Campos adicionais em TRAVEL
alter table public.travel add column if not exists license_plate varchar(20);
alter table public.travel add column if not exists unit_id bigint references public.unit(id) on delete set null;
alter table public.travel add column if not exists occupancy_percentage numeric(5,2) check (occupancy_percentage >= 0 and occupancy_percentage <= 100);

create index if not exists idx_travel_unit_id on public.travel(unit_id);

-- RLS
alter table public.travel         enable row level security;
alter table public.stop           enable row level security;
alter table public.bill           enable row level security;
alter table public.raw_layer      enable row level security;
alter table public.staging_layer  enable row level security;
alter table public.unit           enable row level security;
alter table public.occurrence_category enable row level security;
alter table public.occurrence     enable row level security;

-- Políticas de leitura para usuários autenticados
do $$
begin
  if not exists (select 1 from pg_policies where schemaname='public' and tablename='travel' and policyname='read_authenticated_travel') then
    create policy "read_authenticated_travel" on public.travel for select to authenticated using (true);
  end if;
  if not exists (select 1 from pg_policies where schemaname='public' and tablename='stop' and policyname='read_authenticated_stop') then
    create policy "read_authenticated_stop" on public.stop for select to authenticated using (true);
  end if;
  if not exists (select 1 from pg_policies where schemaname='public' and tablename='bill' and policyname='read_authenticated_bill') then
    create policy "read_authenticated_bill" on public.bill for select to authenticated using (true);
  end if;
  if not exists (select 1 from pg_policies where schemaname='public' and tablename='raw_layer' and policyname='read_authenticated_raw_layer') then
    create policy "read_authenticated_raw_layer" on public.raw_layer for select to authenticated using (true);
  end if;
  if not exists (select 1 from pg_policies where schemaname='public' and tablename='staging_layer' and policyname='read_authenticated_staging_layer') then
    create policy "read_authenticated_staging_layer" on public.staging_layer for select to authenticated using (true);
  end if;
  if not exists (select 1 from pg_policies where schemaname='public' and tablename='unit' and policyname='read_authenticated_unit') then
    create policy "read_authenticated_unit" on public.unit for select to authenticated using (true);
  end if;
  if not exists (select 1 from pg_policies where schemaname='public' and tablename='occurrence_category' and policyname='read_authenticated_occurrence_category') then
    create policy "read_authenticated_occurrence_category" on public.occurrence_category for select to authenticated using (true);
  end if;
  if not exists (select 1 from pg_policies where schemaname='public' and tablename='occurrence' and policyname='read_authenticated_occurrence') then
    create policy "read_authenticated_occurrence" on public.occurrence for select to authenticated using (true);
  end if;
end $$;
`;

async function setupDb() {
  const client = new Client({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false }
  });

  await client.connect();
  try {
    await client.query('begin');
    await client.query(sql);
    await client.query('commit');
    console.log('Banco configurado com sucesso.');
  } catch (err) {
    await client.query('rollback');
    console.error('Falha ao configurar o banco:', err);
    process.exitCode = 1;
  } finally {
    await client.end();
  }
}

setupDb();