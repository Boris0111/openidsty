/**
 * Build-time switch for the public static snapshot (scripts/build-static.mjs sets these); empty in the standalone app.
 * Inlined by Next.js, so the public build carries no runtime configuration.
 */
export const SNAPSHOT_RELEASE=process.env.NEXT_PUBLIC_SNAPSHOT_RELEASE||'';
export const SNAPSHOT_PUBLISHED=process.env.NEXT_PUBLIC_SNAPSHOT_PUBLISHED||'';
export const PUBLIC_SNAPSHOT=Boolean(SNAPSHOT_RELEASE);

/** Taipei calendar date of the snapshot's publication, for the footer and the release notice. */
export function snapshotDate(){
  return SNAPSHOT_PUBLISHED?new Date(SNAPSHOT_PUBLISHED).toLocaleDateString('sv-SE',{timeZone:'Asia/Taipei'}):'';
}
