import { Link } from "react-router-dom";

export default function AboutPage() {
  return (
    <>
      <section className="about-hero">
        <div className="about-copy">
          <p className="eyebrow">Our story</p>
          <h1>About Campus Customs</h1>
          <p className="lead">
            Campus Customs started with a simple idea: the clothes you wear around campus should
            feel like they belong to you.
          </p>
          <p>
            A sweatshirt isn't just a sweatshirt when it's the one you wore to your first
            Harvard-Yale game, or the one you borrowed from your roommate and never gave back.
          </p>
          <p>
            We carry gear for every corner of the Yale community: the residential colleges, the
            graduate and professional schools, and the varsity teams that keep New Haven loud on
            the weekends. Whether you're a first-year, a proud parent, or an alum who still knows
            the words to "Boola Boola," there's something here for you.
          </p>
          <Link to="/products" className="btn-primary">
            Browse the shop
          </Link>
        </div>
        <img
          className="about-photo"
          src="/images/about-sweaters.jpg"
          alt="A stack of soft folded sweaters on a wooden stool in warm window light"
        />
      </section>

      <section className="section">
        <div className="section-head">
          <p className="eyebrow">What we care about</p>
          <h2>Made to be worn, again and again</h2>
        </div>
        <div className="value-cards">
          <article>
            <h3>Comfort first</h3>
            <p>Soft fleece, sturdy cotton, and fits you'll actually want to wear twice a week.</p>
          </article>
          <article>
            <h3>Real campus pride</h3>
            <p>Designs that celebrate the traditions, teams, and places that make Yale feel like home.</p>
          </article>
          <article>
            <h3>Help when you need it</h3>
            <p>
              Not sure about a size or looking for something specific? Our chat assistant is in the
              bottom corner of every page.
            </p>
          </article>
        </div>
        <p className="sign-off">Thanks for shopping with us. Go Bulldogs!</p>
      </section>
    </>
  );
}
