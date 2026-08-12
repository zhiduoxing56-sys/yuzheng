import { NavLink, useSearchParams } from "react-router-dom";

const PAGE_LINKS = [
  { to: "/decision", label: "裁决" },
  { to: "/evidence", label: "证据检索" },
  { to: "/audits", label: "审计记录" },
  { to: "/carla", label: "模拟器" },
];

export function VisualPageNav() {
  const [searchParams] = useSearchParams();
  const turnId = searchParams.get("turn_id")?.trim();
  const pageHref = (path: string) => turnId ? `${path}?${new URLSearchParams({ turn_id: turnId })}` : path;
  return <header className="visual-page-nav">
    <NavLink className="visual-page-brand" to={pageHref("/decision")} aria-label="语证首页">语证</NavLink>
    <nav aria-label="页面导航">
      {PAGE_LINKS.map((link) => <NavLink
        key={link.to}
        to={pageHref(link.to)}
        className={({ isActive }) => isActive ? "visual-page-nav-link is-active" : "visual-page-nav-link"}
      >{link.label}</NavLink>)}
    </nav>
  </header>;
}
