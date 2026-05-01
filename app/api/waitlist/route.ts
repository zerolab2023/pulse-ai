import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function POST(req: NextRequest) {
  const { email, company, role } = await req.json();

  if (!email || !email.includes('@')) {
    return NextResponse.json({ error: 'invalid email' }, { status: 400 });
  }

  const { error } = await supabase
    .from('waitlist')
    .insert({ email: email.trim().toLowerCase(), company: company?.trim() || null, role: role || null });

  if (error) {
    if (error.code === '23505') {
      return NextResponse.json({ ok: true, duplicate: true });
    }
    console.error('waitlist insert error', error);
    return NextResponse.json({ error: 'db error' }, { status: 500 });
  }

  return NextResponse.json({ ok: true });
}
