import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY

export const supabase = createClient(supabaseUrl, supabaseKey)

/**
 * Query a Supabase table directly from the frontend (read-only via publishable key + RLS).
 * Falls back gracefully if Supabase is not configured.
 */
export async function queryTable(table, { select = '*', order, limit, eq } = {}) {
  if (!supabaseUrl || !supabaseKey) return []

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
