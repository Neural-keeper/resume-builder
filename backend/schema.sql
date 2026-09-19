create table if not exists public.master_documents (
  user_id uuid primary key references auth.users(id) on delete cascade,
  document jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

alter table public.master_documents enable row level security;

create policy "Users can manage their own master document"
  on public.master_documents for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger master_documents_updated_at
before update on public.master_documents
for each row execute procedure public.set_updated_at();