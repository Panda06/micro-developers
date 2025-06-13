import { Link, NavLink } from 'react-router-dom'
import '../style/style.css'

export default function Nav({ children }) {
  return (
    <div className="body">
      <header className="header">
        <nav className="header_nav">
          <Link to="/" className="header_logo">
            <img src="/img/logo1.png" alt="" className="header_img" />
            <p className="logo_title">Smart ЖКХ</p>
          </Link>
          <ul className="header_item">
            <li><a href="#"><img src="../img/chat.png" className="logo__img" alt=""/></a></li>
            <li><a href="#"><img src="../img/bell.png" className="logo__img" alt=""/></a></li>
            <li>ALBAGACHIEV ADAM</li>
          </ul>
        </nav>
      </header>

      <main className="main">
        <section className="panel">
          <nav className="panel_nav">
            <ul className="panel_item">
              {[
                { to: '/', icon: 'home.png', title: 'Главное' },
                { to: '/bills', icon: 'bill.png', title: 'Счета' },
                { to: '/history', icon: 'history.png', title: 'История' },
                { to: '/payment', icon: 'payment.png', title: 'Оплата' },
                { to: '/statistics', icon: 'statistics.png', title: 'Статистика' },
              ].map(({to, icon, title}) => (
                <li className="panel_list" key={to}>
                  <NavLink
                    to={to}
                    className={({ isActive }) =>
                      `panel_link${isActive ? ' active' : ''}`
                    }
                  >
                    <img src={`/img/${icon}`} alt="" className="panel_img" />
                    <p className="panel_title">{title}</p>
                  </NavLink>
                </li>
              ))}
            </ul>
            <div className="panel_list">
              <NavLink to="/settings" className="panel_link">
                <img src="/img/setting.png" alt="" className="panel_img" />
                <p className="panel_title">Настройки</p>
              </NavLink>
            </div>
          </nav>
        </section>

        <section className="window">
          {children}
        </section>
      </main>
    </div>
  )
}
