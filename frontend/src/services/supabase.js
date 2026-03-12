import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

/**
 * Query a Supabase table directly from the frontend (read-only via anon key + RLS).
 * Falls back gracefully if Supabase is not configured.
 */
export async function queryTable(table, { select = '*', order, limit, eq } = {}) {
  if (!supabaseUrl || !supabaseAnonKey) return []

  let query = supabase.from(table).select(select)

  if (eq) {
    Object.entries(eq).forEach(([col, val]) => {
      query = query.eq(col, val)
    })
  }
  if (order) {
    query = query.order(order.column, { ascending: order.ascending ?? false })
  }
  if (limit) {
    query = query.limit(limit)
  }

  const { data, error } = await query
  if (error) {
    console.warn(`Supabase query on "${table}" failed:`, error.message)
    return []
  }
  return data
}
